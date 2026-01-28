"""Chat models for in-app messaging."""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ChatThread(Base):
    """Chat thread between customer and handyman for a job."""
    __tablename__ = "chat_threads"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    job_request_id: Mapped[int] = mapped_column(ForeignKey("job_requests.id"), nullable=False)
    
    # Participants (for easy access control)
    customer_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    handyman_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    job_request: Mapped["JobRequest"] = relationship("JobRequest", back_populates="chat_thread")
    messages: Mapped[List["ChatMessage"]] = relationship("ChatMessage", back_populates="thread", order_by="ChatMessage.created_at")


class ChatMessage(Base):
    """Individual message in a chat thread."""
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    thread_id: Mapped[int] = mapped_column(ForeignKey("chat_threads.id"), nullable=False)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # Message content
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Read status (optional for MVP)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    thread: Mapped["ChatThread"] = relationship("ChatThread", back_populates="messages")
