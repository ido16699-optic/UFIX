"""Job requests API endpoints."""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_customer, get_current_handyman
from app.models.user import User, UserRole
from app.models.customer import CustomerProfile
from app.models.handyman import HandymanProfile, ServiceCategory, VerificationStatus
from app.models.job import JobRequest, Offer, JobRequestStatus, OfferStatus
from app.schemas.job import (
    JobRequestCreate,
    JobRequestUpdate,
    JobRequestResponse,
    JobRequestListResponse,
    OfferCreate,
    OfferResponse,
    OfferListResponse,
    OfferAccept,
)

router = APIRouter(prefix="/jobs", tags=["Job Requests"])


# ============ Customer Endpoints ============

@router.post("", response_model=JobRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_job_request(
    job_data: JobRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_customer),
):
    """Create a new job request (customer only)."""
    # Get customer profile
    result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.user_id == current_user.id)
    )
    customer_profile = result.scalar_one_or_none()
    
    if not customer_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer profile not found",
        )
    
    # Create job request
    job_request = JobRequest(
        customer_id=customer_profile.id,
        category=job_data.category,
        title=job_data.title,
        description=job_data.description,
        address=job_data.address,
        latitude=job_data.latitude,
        longitude=job_data.longitude,
        request_type=job_data.request_type,
        scheduled_date=job_data.scheduled_date,
        scheduled_time_window=job_data.scheduled_time_window,
    )
    
    db.add(job_request)
    await db.commit()
    await db.refresh(job_request)
    
    return job_request


@router.get("/my-requests", response_model=JobRequestListResponse)
async def get_my_job_requests(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[JobRequestStatus] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_customer),
):
    """Get customer's own job requests."""
    result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.user_id == current_user.id)
    )
    customer_profile = result.scalar_one_or_none()
    
    if not customer_profile:
        raise HTTPException(status_code=404, detail="Customer profile not found")
    
    # Build query
    query = select(JobRequest).where(JobRequest.customer_id == customer_profile.id)
    count_query = select(func.count(JobRequest.id)).where(JobRequest.customer_id == customer_profile.id)
    
    if status_filter:
        query = query.where(JobRequest.status == status_filter)
        count_query = count_query.where(JobRequest.status == status_filter)
    
    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Get paginated results
    query = query.order_by(JobRequest.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    items = result.scalars().all()
    
    return JobRequestListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{job_id}", response_model=JobRequestResponse)
async def get_job_request(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get job request details."""
    result = await db.execute(
        select(JobRequest)
        .options(selectinload(JobRequest.offers))
        .where(JobRequest.id == job_id)
    )
    job_request = result.scalar_one_or_none()
    
    if not job_request:
        raise HTTPException(status_code=404, detail="Job request not found")
    
    # Check access: customer owner, handyman with offer, or admin
    has_access = False
    if current_user.role == UserRole.ADMIN:
        has_access = True
    elif current_user.role == UserRole.CUSTOMER:
        customer_result = await db.execute(
            select(CustomerProfile).where(CustomerProfile.user_id == current_user.id)
        )
        customer = customer_result.scalar_one_or_none()
        if customer and job_request.customer_id == customer.id:
            has_access = True
    elif current_user.role == UserRole.HANDYMAN:
        # Handyman can see open jobs or jobs they have offered on
        if job_request.status == JobRequestStatus.OPEN:
            has_access = True
        else:
            handyman_result = await db.execute(
                select(HandymanProfile).where(HandymanProfile.user_id == current_user.id)
            )
            handyman = handyman_result.scalar_one_or_none()
            if handyman:
                offer_result = await db.execute(
                    select(Offer).where(
                        and_(
                            Offer.job_request_id == job_id,
                            Offer.handyman_id == handyman.id
                        )
                    )
                )
                if offer_result.scalar_one_or_none():
                    has_access = True
    
    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Add offer count
    offer_count = len(job_request.offers) if job_request.offers else 0
    response = JobRequestResponse.model_validate(job_request)
    response.offer_count = offer_count
    
    return response


# ============ Handyman Endpoints ============

@router.get("/available", response_model=JobRequestListResponse)
async def get_available_jobs(
    category: Optional[ServiceCategory] = None,
    latitude: Optional[float] = Query(None, ge=-90, le=90),
    longitude: Optional[float] = Query(None, ge=-180, le=180),
    radius_km: float = Query(10.0, ge=1, le=100),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_handyman),
):
    """Get available jobs for handyman (open status, matching categories, nearby)."""
    # Get handyman profile
    result = await db.execute(
        select(HandymanProfile).where(HandymanProfile.user_id == current_user.id)
    )
    handyman = result.scalar_one_or_none()
    
    if not handyman:
        raise HTTPException(status_code=404, detail="Handyman profile not found")
    
    # Only verified handymen can see jobs
    if handyman.verification_status != VerificationStatus.APPROVED:
        raise HTTPException(
            status_code=403,
            detail="Verification required to view available jobs",
        )
    
    # Build query for open jobs
    query = select(JobRequest).where(JobRequest.status == JobRequestStatus.OPEN)
    count_query = select(func.count(JobRequest.id)).where(JobRequest.status == JobRequestStatus.OPEN)
    
    # Filter by category if specified
    if category:
        query = query.where(JobRequest.category == category)
        count_query = count_query.where(JobRequest.category == category)
    
    # TODO: Add location-based filtering (requires PostGIS or Haversine formula)
    # For MVP, we'll return all jobs in the category
    
    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Get paginated results
    query = query.order_by(JobRequest.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    items = result.scalars().all()
    
    return JobRequestListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )
