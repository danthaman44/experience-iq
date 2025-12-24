import os
import json
import traceback
import uuid
from dotenv import load_dotenv
# Vercel only supports the deprecated generativeai api
import google.generativeai as genai
from google.generativeai import types

load_dotenv(".env.local")

api_key = os.getenv("GOOGLE_GENERATIVE_AI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel(model_name='gemini-2.5-flash')

def gemini_response(prompt):  
    response = model.generate_content(
        contents=prompt
    )
    return response.text

async def stream_gemini_response(prompt: str):
    """Emit a streaming SSE response from Gemini API."""
    
    def format_sse(payload: dict) -> str:
        return f"data: {json.dumps(payload, separators=(',', ':'))}\n\n"
    
    message_id = f"msg-{uuid.uuid4().hex}"
    text_stream_id = "text-1"
    text_started = False
    
    yield format_sse({"type": "start", "messageId": message_id})
    
    try:
        stream = model.generate_content(
          contents=prompt
        )
        
        for chunk in stream:
            if chunk.text:
                if not text_started:
                    yield format_sse({"type": "text-start", "id": text_stream_id})
                    text_started = True
                yield format_sse({"type": "text-delta", "id": text_stream_id, "delta": chunk.text})
        
        if text_started:
            yield format_sse({"type": "text-end", "id": text_stream_id})
        
        yield format_sse({"type": "finish"})
        yield "data: [DONE]\n\n"
    except Exception as e:
        traceback.print_exc()
        if text_started:
            yield format_sse({"type": "text-end", "id": text_stream_id})
        yield format_sse({"type": "finish"})
        yield "data: [DONE]\n\n"
        raise