"""Chat API endpoints and WebSocket handler."""
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User, UserRole
from app.models.chat import ChatThread, ChatMessage
from app.schemas.chat import (
    ChatMessageCreate,
    ChatMessageResponse,
    ChatThreadResponse,
    ChatThreadWithMessages,
    ChatThreadListResponse,
)

router = APIRouter(prefix="/chat", tags=["Chat"])


# ============ REST Endpoints ============

@router.get("/threads", response_model=ChatThreadListResponse)
async def get_my_chat_threads(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all chat threads for current user."""
    query = select(ChatThread).where(
        or_(
            ChatThread.customer_user_id == current_user.id,
            ChatThread.handyman_user_id == current_user.id,
        )
    ).order_by(ChatThread.updated_at.desc())
    
    result = await db.execute(query)
    threads = result.scalars().all()
    
    # Get last message and unread count for each thread
    thread_responses = []
    for thread in threads:
        # Get last message
        msg_result = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.thread_id == thread.id)
            .order_by(ChatMessage.created_at.desc())
            .limit(1)
        )
        last_message = msg_result.scalar_one_or_none()
        
        # Get unread count
        unread_result = await db.execute(
            select(ChatMessage)
            .where(
                and_(
                    ChatMessage.thread_id == thread.id,
                    ChatMessage.sender_id != current_user.id,
                    ChatMessage.is_read == False,
                )
            )
        )
        unread_messages = unread_result.scalars().all()
        
        thread_response = ChatThreadResponse.model_validate(thread)
        thread_response.last_message = ChatMessageResponse.model_validate(last_message) if last_message else None
        thread_response.unread_count = len(unread_messages)
        thread_responses.append(thread_response)
    
    return ChatThreadListResponse(items=thread_responses, total=len(thread_responses))


@router.get("/threads/{thread_id}", response_model=ChatThreadWithMessages)
async def get_chat_thread(
    thread_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get chat thread with all messages."""
    result = await db.execute(
        select(ChatThread)
        .options(selectinload(ChatThread.messages))
        .where(ChatThread.id == thread_id)
    )
    thread = result.scalar_one_or_none()
    
    if not thread:
        raise HTTPException(status_code=404, detail="Chat thread not found")
    
    # Check access
    if current_user.id not in [thread.customer_user_id, thread.handyman_user_id]:
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Access denied")
    
    # Mark messages as read
    for msg in thread.messages:
        if msg.sender_id != current_user.id and not msg.is_read:
            msg.is_read = True
            msg.read_at = datetime.utcnow()
    
    await db.commit()
    
    return thread


@router.post("/threads/{thread_id}/messages", response_model=ChatMessageResponse)
async def send_message(
    thread_id: int,
    message_data: ChatMessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send a message in a chat thread."""
    result = await db.execute(
        select(ChatThread).where(ChatThread.id == thread_id)
    )
    thread = result.scalar_one_or_none()
    
    if not thread:
        raise HTTPException(status_code=404, detail="Chat thread not found")
    
    # Check access
    if current_user.id not in [thread.customer_user_id, thread.handyman_user_id]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not thread.is_active:
        raise HTTPException(status_code=400, detail="Chat thread is closed")
    
    # Create message
    message = ChatMessage(
        thread_id=thread_id,
        sender_id=current_user.id,
        content=message_data.content,
    )
    db.add(message)
    
    # Update thread timestamp
    thread.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(message)
    
    return message


# ============ WebSocket Handler ============

# Connection manager for WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, List[WebSocket]] = {}  # user_id -> connections
    
    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
    
    async def send_to_user(self, user_id: int, message: dict):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await connection.send_json(message)


manager = ConnectionManager()


@router.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    """WebSocket endpoint for real-time chat."""
    from app.core.security import decode_access_token
    
    # Verify token
    payload = decode_access_token(token)
    if not payload:
        await websocket.close(code=4001)
        return
    
    user_id = payload.get("sub")
    if not user_id:
        await websocket.close(code=4001)
        return
    
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            # Handle different message types
            msg_type = data.get("type")
            
            if msg_type == "message":
                # Process and broadcast message
                thread_id = data.get("thread_id")
                content = data.get("content")
                
                # Get thread and recipient from database
                # (simplified - in production, use dependency injection)
                async for db in get_db():
                    result = await db.execute(
                        select(ChatThread).where(ChatThread.id == thread_id)
                    )
                    thread = result.scalar_one_or_none()
                    
                    if thread and user_id in [thread.customer_user_id, thread.handyman_user_id]:
                        # Save message
                        message = ChatMessage(
                            thread_id=thread_id,
                            sender_id=user_id,
                            content=content,
                        )
                        db.add(message)
                        await db.commit()
                        await db.refresh(message)
                        
                        # Send to recipient
                        recipient_id = (
                            thread.handyman_user_id 
                            if user_id == thread.customer_user_id 
                            else thread.customer_user_id
                        )
                        
                        await manager.send_to_user(recipient_id, {
                            "type": "new_message",
                            "thread_id": thread_id,
                            "message": {
                                "id": message.id,
                                "sender_id": message.sender_id,
                                "content": message.content,
                                "created_at": message.created_at.isoformat(),
                            }
                        })
            
            elif msg_type == "typing":
                # Broadcast typing indicator
                thread_id = data.get("thread_id")
                async for db in get_db():
                    result = await db.execute(
                        select(ChatThread).where(ChatThread.id == thread_id)
                    )
                    thread = result.scalar_one_or_none()
                    
                    if thread:
                        recipient_id = (
                            thread.handyman_user_id 
                            if user_id == thread.customer_user_id 
                            else thread.customer_user_id
                        )
                        await manager.send_to_user(recipient_id, {
                            "type": "typing",
                            "thread_id": thread_id,
                            "user_id": user_id,
                        })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
