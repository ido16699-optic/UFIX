"""Offers API endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_customer, get_current_handyman
from app.models.user import User, UserRole
from app.models.customer import CustomerProfile
from app.models.handyman import HandymanProfile, VerificationStatus
from app.models.job import JobRequest, Offer, JobRequestStatus, OfferStatus
from app.models.order import Order, OrderStatus
from app.models.chat import ChatThread
from app.schemas.job import OfferCreate, OfferResponse, OfferListResponse, OfferAccept

router = APIRouter(prefix="/offers", tags=["Offers"])


@router.post("", response_model=OfferResponse, status_code=status.HTTP_201_CREATED)
async def create_offer(
    offer_data: OfferCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_handyman),
):
    """Create an offer for a job request (handyman only)."""
    # Get handyman profile
    result = await db.execute(
        select(HandymanProfile).where(HandymanProfile.user_id == current_user.id)
    )
    handyman = result.scalar_one_or_none()
    
    if not handyman:
        raise HTTPException(status_code=404, detail="Handyman profile not found")
    
    # Check verification status
    if handyman.verification_status != VerificationStatus.APPROVED:
        raise HTTPException(
            status_code=403,
            detail="Verification required to create offers",
        )
    
    # Get job request
    result = await db.execute(
        select(JobRequest).where(JobRequest.id == offer_data.job_request_id)
    )
    job_request = result.scalar_one_or_none()
    
    if not job_request:
        raise HTTPException(status_code=404, detail="Job request not found")
    
    if job_request.status != JobRequestStatus.OPEN:
        raise HTTPException(
            status_code=400,
            detail="Job request is not accepting offers",
        )
    
    # Check if handyman already has an offer for this job
    result = await db.execute(
        select(Offer).where(
            and_(
                Offer.job_request_id == offer_data.job_request_id,
                Offer.handyman_id == handyman.id,
                Offer.status.in_([OfferStatus.PENDING, OfferStatus.ACCEPTED])
            )
        )
    )
    existing_offer = result.scalar_one_or_none()
    
    if existing_offer:
        raise HTTPException(
            status_code=400,
            detail="You already have an active offer for this job",
        )
    
    # Create offer
    offer = Offer(
        job_request_id=offer_data.job_request_id,
        handyman_id=handyman.id,
        price=offer_data.price,
        message=offer_data.message,
        estimated_arrival_minutes=offer_data.estimated_arrival_minutes,
        available_date=offer_data.available_date,
        available_time_window=offer_data.available_time_window,
    )
    
    db.add(offer)
    await db.commit()
    await db.refresh(offer)
    
    return offer


@router.get("/job/{job_id}", response_model=OfferListResponse)
async def get_offers_for_job(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all offers for a job request."""
    # Get job request
    result = await db.execute(
        select(JobRequest).where(JobRequest.id == job_id)
    )
    job_request = result.scalar_one_or_none()
    
    if not job_request:
        raise HTTPException(status_code=404, detail="Job request not found")
    
    # Check access
    if current_user.role == UserRole.CUSTOMER:
        customer_result = await db.execute(
            select(CustomerProfile).where(CustomerProfile.user_id == current_user.id)
        )
        customer = customer_result.scalar_one_or_none()
        if not customer or job_request.customer_id != customer.id:
            raise HTTPException(status_code=403, detail="Access denied")
    elif current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get offers with handyman profiles
    result = await db.execute(
        select(Offer)
        .options(selectinload(Offer.handyman).selectinload(HandymanProfile.user))
        .where(Offer.job_request_id == job_id)
        .order_by(Offer.created_at.desc())
    )
    offers = result.scalars().all()
    
    return OfferListResponse(items=offers, total=len(offers))


@router.post("/{offer_id}/accept", response_model=OfferResponse)
async def accept_offer(
    offer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_customer),
):
    """Accept an offer (customer only)."""
    # Get offer with job request
    result = await db.execute(
        select(Offer)
        .options(selectinload(Offer.job_request))
        .where(Offer.id == offer_id)
    )
    offer = result.scalar_one_or_none()
    
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    
    # Check that customer owns the job request
    customer_result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.user_id == current_user.id)
    )
    customer = customer_result.scalar_one_or_none()
    
    if not customer or offer.job_request.customer_id != customer.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if offer.status != OfferStatus.PENDING:
        raise HTTPException(status_code=400, detail="Offer is no longer pending")
    
    if offer.job_request.status != JobRequestStatus.OPEN:
        raise HTTPException(status_code=400, detail="Job request is no longer accepting offers")
    
    # Accept this offer
    offer.status = OfferStatus.ACCEPTED
    
    # Reject all other pending offers for this job
    await db.execute(
        select(Offer).where(
            and_(
                Offer.job_request_id == offer.job_request_id,
                Offer.id != offer_id,
                Offer.status == OfferStatus.PENDING
            )
        )
    )
    
    # Update job request status
    offer.job_request.status = JobRequestStatus.MATCHED
    
    # Create order
    order = Order(
        job_request_id=offer.job_request_id,
        offer_id=offer.id,
        status=OrderStatus.PENDING_PAYMENT,
    )
    db.add(order)
    
    # Create chat thread
    handyman_result = await db.execute(
        select(HandymanProfile).where(HandymanProfile.id == offer.handyman_id)
    )
    handyman = handyman_result.scalar_one()
    
    chat_thread = ChatThread(
        job_request_id=offer.job_request_id,
        customer_user_id=current_user.id,
        handyman_user_id=handyman.user_id,
    )
    db.add(chat_thread)
    
    await db.commit()
    await db.refresh(offer)
    
    return offer


@router.post("/{offer_id}/reject", response_model=OfferResponse)
async def reject_offer(
    offer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_customer),
):
    """Reject an offer (customer only)."""
    result = await db.execute(
        select(Offer)
        .options(selectinload(Offer.job_request))
        .where(Offer.id == offer_id)
    )
    offer = result.scalar_one_or_none()
    
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    
    # Check access
    customer_result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.user_id == current_user.id)
    )
    customer = customer_result.scalar_one_or_none()
    
    if not customer or offer.job_request.customer_id != customer.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if offer.status != OfferStatus.PENDING:
        raise HTTPException(status_code=400, detail="Offer is no longer pending")
    
    offer.status = OfferStatus.REJECTED
    await db.commit()
    await db.refresh(offer)
    
    return offer


@router.get("/my-offers", response_model=OfferListResponse)
async def get_my_offers(
    status_filter: Optional[OfferStatus] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_handyman),
):
    """Get handyman's own offers."""
    result = await db.execute(
        select(HandymanProfile).where(HandymanProfile.user_id == current_user.id)
    )
    handyman = result.scalar_one_or_none()
    
    if not handyman:
        raise HTTPException(status_code=404, detail="Handyman profile not found")
    
    query = select(Offer).where(Offer.handyman_id == handyman.id)
    
    if status_filter:
        query = query.where(Offer.status == status_filter)
    
    query = query.order_by(Offer.created_at.desc())
    
    result = await db.execute(query)
    offers = result.scalars().all()
    
    return OfferListResponse(items=offers, total=len(offers))
