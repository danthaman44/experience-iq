from pydantic import BaseModel
from typing import List, Literal

class ClientAttachment(BaseModel):
    name: str
    contentType: str
    url: str

# Define the message models to match AI SDK UI format
class MessagePart(BaseModel):
    type: Literal["text", "tool-call", "tool-result"]
    text: str | None = None

class UIMessage(BaseModel):
    id: str
    role: Literal["user", "assistant"]
    parts: List[MessagePart]

class ChatHistoryResponse(BaseModel):
    messages: List[UIMessage]
