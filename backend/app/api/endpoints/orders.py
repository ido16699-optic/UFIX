"""Orders and Payments API endpoints."""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.config import settings
from app.api.deps import get_current_user, get_current_customer, get_current_handyman
from app.models.user import User, UserRole
from app.models.customer import CustomerProfile
from app.models.handyman import HandymanProfile
from app.models.job import JobRequest, Offer, JobRequestStatus
from app.models.order import Order, Payment, OrderStatus, PaymentStatus
from app.schemas.order import (
    OrderResponse,
    OrderStatusUpdate,
    OrderListResponse,
    PaymentIntentCreate,
    PaymentIntentResponse,
    PaymentResponse,
    PaymentConfirm,
)

router = APIRouter(tags=["Orders & Payments"])


# ============ Orders Endpoints ============

@router.get("/orders", response_model=OrderListResponse)
async def get_my_orders(
    status_filter: Optional[OrderStatus] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's orders (customer or handyman)."""
    query = select(Order).options(
        selectinload(Order.job_request),
        selectinload(Order.offer),
    )
    
    if current_user.role == UserRole.CUSTOMER:
        # Get customer's orders
        customer_result = await db.execute(
            select(CustomerProfile).where(CustomerProfile.user_id == current_user.id)
        )
        customer = customer_result.scalar_one_or_none()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer profile not found")
        
        query = query.join(JobRequest).where(JobRequest.customer_id == customer.id)
        
    elif current_user.role == UserRole.HANDYMAN:
        # Get handyman's orders
        handyman_result = await db.execute(
            select(HandymanProfile).where(HandymanProfile.user_id == current_user.id)
        )
        handyman = handyman_result.scalar_one_or_none()
        if not handyman:
            raise HTTPException(status_code=404, detail="Handyman profile not found")
        
        query = query.join(Offer).where(Offer.handyman_id == handyman.id)
    
    else:
        # Admin can see all
        pass
    
    if status_filter:
        query = query.where(Order.status == status_filter)
    
    # Count total
    count_query = select(Order.id)
    # Apply same filters... (simplified for MVP)
    
    query = query.order_by(Order.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    orders = result.scalars().all()
    
    return OrderListResponse(
        items=orders,
        total=len(orders),  # Simplified for MVP
        page=page,
        page_size=page_size,
    )


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get order details."""
    result = await db.execute(
        select(Order)
        .options(
            selectinload(Order.job_request),
            selectinload(Order.offer),
        )
        .where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check access
    if current_user.role != UserRole.ADMIN:
        has_access = False
        
        if current_user.role == UserRole.CUSTOMER:
            customer_result = await db.execute(
                select(CustomerProfile).where(CustomerProfile.user_id == current_user.id)
            )
            customer = customer_result.scalar_one_or_none()
            if customer and order.job_request.customer_id == customer.id:
                has_access = True
                
        elif current_user.role == UserRole.HANDYMAN:
            handyman_result = await db.execute(
                select(HandymanProfile).where(HandymanProfile.user_id == current_user.id)
            )
            handyman = handyman_result.scalar_one_or_none()
            if handyman and order.offer.handyman_id == handyman.id:
                has_access = True
        
        if not has_access:
            raise HTTPException(status_code=403, detail="Access denied")
    
    return order


@router.patch("/orders/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update order status (for job progress tracking)."""
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.offer), selectinload(Order.job_request))
        .where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Validate status transitions
    valid_transitions = {
        OrderStatus.PENDING_PAYMENT: [OrderStatus.PAYMENT_AUTHORIZED, OrderStatus.CANCELLED],
        OrderStatus.PAYMENT_AUTHORIZED: [OrderStatus.IN_PROGRESS, OrderStatus.CANCELLED],
        OrderStatus.IN_PROGRESS: [OrderStatus.COMPLETED, OrderStatus.DISPUTED],
        OrderStatus.COMPLETED: [],  # Final state
        OrderStatus.CANCELLED: [],  # Final state
        OrderStatus.DISPUTED: [OrderStatus.COMPLETED, OrderStatus.CANCELLED],
    }
    
    if status_update.status not in valid_transitions.get(order.status, []):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot transition from {order.status} to {status_update.status}",
        )
    
    # Role-based status update restrictions
    if current_user.role == UserRole.HANDYMAN:
        # Handyman can start job and mark complete
        allowed = [OrderStatus.IN_PROGRESS, OrderStatus.COMPLETED]
        if status_update.status not in allowed:
            raise HTTPException(status_code=403, detail="Not authorized for this status change")
    elif current_user.role == UserRole.CUSTOMER:
        # Customer can cancel or dispute
        allowed = [OrderStatus.CANCELLED, OrderStatus.DISPUTED]
        if status_update.status not in allowed:
            raise HTTPException(status_code=403, detail="Not authorized for this status change")
    
    # Update status
    order.status = status_update.status
    
    if status_update.status == OrderStatus.IN_PROGRESS:
        order.started_at = datetime.utcnow()
        order.job_request.status = JobRequestStatus.IN_PROGRESS
    elif status_update.status == OrderStatus.COMPLETED:
        order.completed_at = datetime.utcnow()
        order.job_request.status = JobRequestStatus.COMPLETED
        
        # Update handyman stats
        handyman_result = await db.execute(
            select(HandymanProfile).where(HandymanProfile.id == order.offer.handyman_id)
        )
        handyman = handyman_result.scalar_one()
        handyman.total_completed_jobs += 1
        
        # Update payment status
        if order.payment:
            order.payment.status = PaymentStatus.PAYOUT_READY
    elif status_update.status == OrderStatus.CANCELLED:
        order.job_request.status = JobRequestStatus.CANCELLED
    
    await db.commit()
    await db.refresh(order)
    
    return order


# ============ Payments Endpoints ============

@router.post("/payments/create-intent", response_model=PaymentIntentResponse)
async def create_payment_intent(
    payment_data: PaymentIntentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_customer),
):
    """Create a payment intent for an order."""
    # Get order
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.offer), selectinload(Order.job_request))
        .where(Order.id == payment_data.order_id)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check ownership
    customer_result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.user_id == current_user.id)
    )
    customer = customer_result.scalar_one_or_none()
    
    if not customer or order.job_request.customer_id != customer.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if order.status != OrderStatus.PENDING_PAYMENT:
        raise HTTPException(status_code=400, detail="Order is not awaiting payment")
    
    # Calculate amounts
    amount = order.offer.price
    commission, handyman_payout = Payment.calculate_commission(amount)
    
    # For MVP, simulate Stripe payment intent
    # In production, use: stripe.PaymentIntent.create(...)
    payment_intent_id = f"pi_test_{order.id}_{int(datetime.utcnow().timestamp())}"
    client_secret = f"{payment_intent_id}_secret_test"
    
    # Create payment record
    payment = Payment(
        order_id=order.id,
        provider="stripe",
        provider_payment_id=payment_intent_id,
        amount=amount,
        commission=commission,
        handyman_payout=handyman_payout,
        status=PaymentStatus.PENDING,
    )
    db.add(payment)
    await db.commit()
    
    return PaymentIntentResponse(
        client_secret=client_secret,
        payment_intent_id=payment_intent_id,
        amount=amount,
        currency="usd",
    )


@router.post("/payments/confirm", response_model=PaymentResponse)
async def confirm_payment(
    payment_confirm: PaymentConfirm,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_customer),
):
    """Confirm a payment (after Stripe processes it)."""
    # Find payment by intent ID
    result = await db.execute(
        select(Payment)
        .options(selectinload(Payment.order).selectinload(Order.job_request))
        .where(Payment.provider_payment_id == payment_confirm.payment_intent_id)
    )
    payment = result.scalar_one_or_none()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Verify ownership
    customer_result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.user_id == current_user.id)
    )
    customer = customer_result.scalar_one_or_none()
    
    if not customer or payment.order.job_request.customer_id != customer.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # For MVP, simulate successful payment
    # In production, verify with Stripe
    payment.status = PaymentStatus.AUTHORIZED
    payment.order.status = OrderStatus.PAYMENT_AUTHORIZED
    
    await db.commit()
    await db.refresh(payment)
    
    return payment
