"""Pydantic schemas for Orders and Payments."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.models.order import OrderStatus, PaymentStatus
from app.schemas.job import JobRequestResponse, OfferResponse


# ============ Order Schemas ============

class OrderResponse(BaseModel):
    """Order response."""
    id: int
    job_request_id: int
    offer_id: int
    status: OrderStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    job_request: Optional[JobRequestResponse] = None
    offer: Optional[OfferResponse] = None

    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    """Schema for updating order status."""
    status: OrderStatus


class OrderListResponse(BaseModel):
    """List of orders with pagination."""
    items: list[OrderResponse]
    total: int
    page: int
    page_size: int


# ============ Payment Schemas ============

class PaymentIntentCreate(BaseModel):
    """Schema for creating a payment intent."""
    order_id: int


class PaymentIntentResponse(BaseModel):
    """Payment intent response (from Stripe)."""
    client_secret: str
    payment_intent_id: str
    amount: float
    currency: str = "usd"


class PaymentResponse(BaseModel):
    """Payment response."""
    id: int
    order_id: int
    provider: str
    amount: float
    commission: float
    handyman_payout: float
    status: PaymentStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaymentConfirm(BaseModel):
    """Schema for confirming payment."""
    payment_intent_id: str
