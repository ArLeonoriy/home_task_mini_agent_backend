from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class ChatResponse(BaseModel):
    id: int
    created_at: datetime

class MessageRequest(BaseModel):
    content: str = Field(..., min_length=1)

class AssistantMessage(BaseModel):
    role: str = "assistant"
    content: str

class SendMessageResponse(BaseModel):
    chat_id: int
    assistant_message: AssistantMessage

class MessageResponse(BaseModel):
    role: str
    content: str

class AgentEventResponse(BaseModel):
    event_type: str
    tool_name: str
    payload: dict

class TicketResponse(BaseModel):
    id: int
    chat_id: int
    order_id: Optional[int]
    text: str
    status: str
    created_at: datetime

class TicketUpdateRequest(BaseModel):
    status: str = Field(..., pattern="^(open|in_progress|closed)$")

class FAQItemResponse(BaseModel):
    id: int
    slug: str
    question: str
    answer: str
    tags: str