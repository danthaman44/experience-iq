import os
import json
import traceback
import uuid
import tempfile
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.types import File
from .prompt import system_prompt
from .supabase import create_message, get_messages, Message
from fastapi import UploadFile, File, HTTPException
from .logging import log_info
from .tools import get_message_history_function
from google.adk.runners import Runner
from google.adk.models import Gemini
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB size limit
MAX_OUTPUT_TOKENS = 512
GEMINI_MODEL = "gemini-2.5-flash-lite"
DEFAULT_TEMPERATURE = 0.5
MOCK_USER_ID = "test_user_123"
APP_NAME = "agents"

load_dotenv(".env.local")
api_key = os.getenv("GOOGLE_GENERATIVE_AI_API_KEY")
client = genai.Client(api_key=api_key)
tools = types.Tool(function_declarations=[get_message_history_function])
adk_model = Gemini(model=GEMINI_MODEL)
adk_model.api_client = client
session_service = InMemorySessionService() # Use InMemorySessionService for local testing

root_agent = Agent(
    name="resume_feedback_agent",
    model=adk_model,
    description="Agent that provides helpful resume feedback and suggestions.",
    instruction=system_prompt(),
    tools=[],
)

def gemini_response(prompt):  
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt(),
            max_output_tokens=MAX_OUTPUT_TOKENS,
            temperature=DEFAULT_TEMPERATURE,
        )
    )
    return response.text

async def handle_function_call(thread_id: str, user_message: str, resume: File) -> str:
    # The history retrieved by your tool call:
    retrieved_history = []
    past_messages = await get_messages(thread_id)
    for past_message in past_messages[::-1]:
        retrieved_history.append({"role": past_message["sender"], "parts": [{"text": past_message["content"]}]})

    # The subsequent API call
    chat = client.chats.create(
        model=GEMINI_MODEL,
        config={
            "system_instruction": system_prompt(),
            "max_output_tokens": MAX_OUTPUT_TOKENS,
            "temperature": DEFAULT_TEMPERATURE,
        },
        history=retrieved_history # Pass your tool-retrieved messages here
    )
    response = chat.send_message([user_message, resume])
    return response.text

async def stream_gemini_response(prompt: str, session_id: str, file_reference: str):
    """Emit a streaming SSE response from Gemini API."""
    
    def format_sse(payload: dict) -> str:
        return f"data: {json.dumps(payload, separators=(',', ':'))}\n\n"
    
    message_id = f"msg-{uuid.uuid4().hex}"
    text_stream_id = "text-1"
    text_started = False
    
    yield format_sse({"type": "start", "messageId": message_id})

    retrieved_file = client.files.get(name=file_reference)
    log_info(f"Retrieved file: {retrieved_file.name}")

    # Register the session ID with the service
    try:
        session = await session_service.get_session(
            app_name=APP_NAME,
            user_id=MOCK_USER_ID,
            session_id=session_id
        )
        if not session:
            await session_service.create_session(
                app_name=APP_NAME,
                user_id=MOCK_USER_ID,
                session_id=session_id
            )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error getting session: {e}")

    try:
        runner = Runner(
            agent=root_agent, 
            session_service=session_service, 
            app_name=APP_NAME
        )
        response = runner.run(
            new_message=Content(parts=[Part(text=prompt)]),
            user_id=MOCK_USER_ID,
            session_id=session_id)

        accumulated_content = ""

        for chunk in response:
            # Extract text from Event.content.parts
            chunk_text = None
            if chunk.content and chunk.content.parts:
                text_parts = [part.text for part in chunk.content.parts if hasattr(part, 'text') and part.text]
                chunk_text = ''.join(text_parts) if text_parts else None

            if chunk_text:
                accumulated_content += chunk_text
                if not text_started:
                    yield format_sse({"type": "text-start", "id": text_stream_id})
                    text_started = True
                yield format_sse({"type": "text-delta", "id": text_stream_id, "delta": chunk_text}) 

        if text_started:
            yield format_sse({"type": "text-end", "id": text_stream_id})
        
        # Save the entire accumulated stream as a single message
        if accumulated_content:
            await create_message(message=Message(thread_id=session_id, sender="model", content=accumulated_content))
        
        yield format_sse({"type": "finish"})
        yield "data: [DONE]\n\n"
    except Exception as e:
        traceback.print_exc()
        if text_started:
            yield format_sse({"type": "text-end", "id": text_stream_id})
        yield format_sse({"type": "finish"})
        yield "data: [DONE]\n\n"
        raise

async def upload_file_to_gemini(file: UploadFile = File(...)):
    if file.size > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="File size exceeds the allowed limit")
    
    # Create a temporary file with the same extension
    suffix = os.path.splitext(file.filename)[1] if file.filename else ""
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        # Write the uploaded file content to the temp file
        content = await file.read()
        temp_file.write(content)
        temp_path = temp_file.name
    
    try:
        # Upload the resume using the Files API
        gemini_file = client.files.upload(file=temp_path)

        # Wait for the file to finish processing
        while gemini_file.state.name == 'PROCESSING':
            time.sleep(1)
            gemini_file = client.files.get(name=gemini_file.name)

        return gemini_file
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error uploading file: {e}")
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_path):
            os.unlink(temp_path)