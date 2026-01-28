"""Pydantic schemas for Chat functionality."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ============ Chat Message Schemas ============

class ChatMessageCreate(BaseModel):
    """Schema for sending a chat message."""
    content: str = Field(..., min_length=1, max_length=2000)


class ChatMessageResponse(BaseModel):
    """Chat message response."""
    id: int
    thread_id: int
    sender_id: int
    content: str
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Chat Thread Schemas ============

class ChatThreadResponse(BaseModel):
    """Chat thread response."""
    id: int
    job_request_id: int
    customer_user_id: int
    handyman_user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_message: Optional[ChatMessageResponse] = None
    unread_count: Optional[int] = None

    class Config:
        from_attributes = True


class ChatThreadWithMessages(ChatThreadResponse):
    """Chat thread with all messages."""
    messages: List[ChatMessageResponse] = []


class ChatThreadListResponse(BaseModel):
    """List of chat threads."""
    items: List[ChatThreadResponse]
    total: int


# ============ WebSocket Message Schemas ============

class WebSocketMessage(BaseModel):
    """WebSocket message format."""
    type: str  # "message", "typing", "read"
    thread_id: int
    content: Optional[str] = None
    message_id: Optional[int] = None


class WebSocketEvent(BaseModel):
    """WebSocket event sent to clients."""
    type: str
    data: dict
