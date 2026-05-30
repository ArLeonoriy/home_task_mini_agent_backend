from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base

class Chat(Base):
    __tablename__ = "chats"
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    messages = relationship("Message", back_populates="chat", order_by="Message.created_at")
    events = relationship("AgentEvent", back_populates="chat", order_by="AgentEvent.created_at")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), index=True)
    role = Column(String)   # user, assistant, tool
    content = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    chat = relationship("Chat", back_populates="messages")

class AgentEvent(Base):
    __tablename__ = "agent_events"
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), index=True)
    event_type = Column(String)  # tool_call, tool_result
    tool_name = Column(String)
    payload = Column(Text)       # JSON строка
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    chat = relationship("Chat", back_populates="events")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    status = Column(String)
    title = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer)
    order_id = Column(Integer, nullable=True)
    text = Column(Text)
    status = Column(String, default="open")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class FAQItem(Base):
    __tablename__ = "faq_items"
    id = Column(Integer, primary_key=True)
    slug = Column(String, unique=True)
    question = Column(Text)
    answer = Column(Text)
    tags = Column(Text)