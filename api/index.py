from typing import List, Optional
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi import FastAPI, Query, Request as FastAPIRequest, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
import uuid as uuid_lib
from .utils.prompt import ClientMessage
from .utils.stream import patch_response_with_headers, stream_resume_required_message
from .utils.gemini import gemini_response, stream_gemini_response
from vercel.headers import set_headers
from .utils.supabase import (
    Message,
    create_message,
    get_messages,
    get_resume,
    get_job_description,
)
from .utils.model import ChatHistoryResponse, UIMessage, MessagePart
from .resume import router as resume_router
from .job_description import router as job_description_router

load_dotenv(".env.local")

app = FastAPI()
app.include_router(resume_router)
app.include_router(job_description_router)


@app.middleware("http")
async def _vercel_set_headers(request: FastAPIRequest, call_next):
    set_headers(dict(request.headers))
    return await call_next(request)


class Request(BaseModel):
    messages: List[ClientMessage]
    id: Optional[str] = None


class PromptRequest(BaseModel):
    prompt: str


# Health check
@app.get("/api/health")
async def health_check():
    return JSONResponse(content={"status": "healthy"}, status_code=200)


# Test endpoint to generate a response from Gemini API
@app.post("/api/generate")
async def generate_response(request: PromptRequest):
    try:
        response = gemini_response(request.prompt)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling Gemini API: {e}")


# Chat endpoint to handle chat data
@app.post("/api/chat")
async def handle_chat_data(request: Request, protocol: str = Query("data")):
    # Extract the message content from the last message in the conversation
    if not request.messages:
        raise HTTPException(status_code=400, detail="No messages provided")

    last_message = request.messages[-1]
    prompt = last_message.content or ""

    if not prompt and last_message.parts:
        # Extract text from parts if content is not directly available
        text_parts = [part.text for part in last_message.parts if part.text]
        prompt = " ".join(text_parts)

    if not prompt:
        raise HTTPException(status_code=400, detail="No message content found")

    # Use UUID from request if provided, otherwise generate a random UUID
    thread_id = request.id if request.id else str(uuid_lib.uuid4())

    # Create user message
    await create_message(
        message=Message(thread_id=thread_id, sender="user", content=prompt)
    )

    resume = await get_resume(thread_id)
    if not resume:
        # Stream AI system message asking to upload resume
        response = StreamingResponse(
            stream_resume_required_message(thread_id), media_type="text/event-stream"
        )
        return patch_response_with_headers(response, protocol)

    # Get job description if available (optional)
    job_description = await get_job_description(thread_id)
    job_description_reference = job_description[0]["name"] if job_description else None

    response = StreamingResponse(
        stream_gemini_response(
            prompt, thread_id, resume[0]["name"], job_description_reference
        ),
        media_type="text/event-stream",
    )
    return patch_response_with_headers(response, protocol)


# Get chat history
@app.get("/api/chat/history/{thread_id}", response_model=ChatHistoryResponse)
async def get_chat_history(thread_id: str):
    """
    Fetch messages for a specific chat thread
    """
    try:
        ui_messages = []
        stored_messages = await get_messages(thread_id)
        for message in stored_messages:
            sender = "assistant" if message["sender"] == "model" else "user"
            ui_messages.append(
                UIMessage(
                    id=str(message["id"]),
                    role=sender,
                    parts=[MessagePart(type="text", text=message["content"])],
                )
            )
        return ChatHistoryResponse(messages=ui_messages[::-1])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
