from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Chat, Message, AgentEvent
from ..schemas import (
    ChatResponse, MessageRequest, SendMessageResponse,
    MessageResponse, AgentEventResponse, AssistantMessage
)
from ..services.message_processor import process_message
import json

router = APIRouter(prefix="/chats", tags=["chats"])

@router.post("", response_model=ChatResponse, status_code=201)
def create_chat(db: Session = Depends(get_db)):
    chat = Chat()
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat

@router.get("/{chat_id}", response_model=ChatResponse)
def get_chat(chat_id: int, db: Session = Depends(get_db)):
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Чат не найден")
    return chat

@router.post("/{chat_id}/messages", response_model=SendMessageResponse)
def send_message(chat_id: int, req: MessageRequest, db: Session = Depends(get_db)):
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Чат не найден")

    assistant_content = process_message(db, chat_id, req.content)
    return SendMessageResponse(
        chat_id=chat_id,
        assistant_message=AssistantMessage(content=assistant_content)
    )

@router.get("/{chat_id}/messages", response_model=list[MessageResponse])
def get_messages(chat_id: int, db: Session = Depends(get_db)):
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Чат не найден")
    messages = db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.created_at).all()
    return [MessageResponse(role=m.role, content=m.content) for m in messages]

@router.get("/{chat_id}/events", response_model=list[AgentEventResponse])
def get_agent_events(
    chat_id: int,
    event_type: str = Query(None, description="Фильтр по типу события (tool_call, tool_result)"),
    db: Session = Depends(get_db)
):
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Чат не найден")
    query = db.query(AgentEvent).filter(AgentEvent.chat_id == chat_id)
    if event_type:
        query = query.filter(AgentEvent.event_type == event_type)
    events = query.order_by(AgentEvent.created_at).all()
    return [
        AgentEventResponse(
            event_type=e.event_type,
            tool_name=e.tool_name,
            payload=json.loads(e.payload)
        ) for e in events
    ]