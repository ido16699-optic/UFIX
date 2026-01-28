"""Admin API endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from datetime import datetime

from app.core.database import get_db
from app.api.deps import get_current_admin
from app.models.user import User, UserRole
from app.models.handyman import HandymanProfile, VerificationDocument, VerificationStatus
from app.models.job import JobRequest
from app.models.order import Order, OrderStatus, Payment
from app.schemas.handyman import VerificationDocumentResponse, VerificationReview, HandymanProfileResponse

router = APIRouter(prefix="/admin", tags=["Admin"])


# ============ Verification Management ============

@router.get("/verifications/pending", response_model=list[VerificationDocumentResponse])
async def get_pending_verifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Get all pending verification documents."""
    result = await db.execute(
        select(VerificationDocument)
        .options(selectinload(VerificationDocument.handyman).selectinload(HandymanProfile.user))
        .where(VerificationDocument.status == VerificationStatus.PENDING)
        .order_by(VerificationDocument.created_at.asc())
    )
    documents = result.scalars().all()
    return documents


@router.get("/verifications/{doc_id}", response_model=VerificationDocumentResponse)
async def get_verification_document(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Get a specific verification document."""
    result = await db.execute(
        select(VerificationDocument)
        .options(selectinload(VerificationDocument.handyman).selectinload(HandymanProfile.user))
        .where(VerificationDocument.id == doc_id)
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document


@router.post("/verifications/{doc_id}/review", response_model=VerificationDocumentResponse)
async def review_verification(
    doc_id: int,
    review: VerificationReview,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Approve or reject a verification document."""
    result = await db.execute(
        select(VerificationDocument)
        .options(selectinload(VerificationDocument.handyman))
        .where(VerificationDocument.id == doc_id)
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document.status != VerificationStatus.PENDING:
        raise HTTPException(status_code=400, detail="Document already reviewed")
    
    # Update document
    document.status = review.status
    document.reviewed_by_admin_id = current_user.id
    document.review_notes = review.review_notes
    document.reviewed_at = datetime.utcnow()
    
    # Update handyman profile verification status
    if review.status == VerificationStatus.APPROVED:
        document.handyman.verification_status = VerificationStatus.APPROVED
    elif review.status == VerificationStatus.REJECTED:
        # Only set rejected if no other approved documents
        other_approved = await db.execute(
            select(VerificationDocument).where(
                VerificationDocument.handyman_id == document.handyman_id,
                VerificationDocument.id != doc_id,
                VerificationDocument.status == VerificationStatus.APPROVED,
            )
        )
        if not other_approved.scalar_one_or_none():
            document.handyman.verification_status = VerificationStatus.REJECTED
    
    await db.commit()
    await db.refresh(document)
    
    return document


# ============ Platform Metrics ============

@router.get("/metrics")
async def get_platform_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Get basic platform metrics."""
    # User counts
    user_count = await db.execute(select(func.count(User.id)))
    customer_count = await db.execute(
        select(func.count(User.id)).where(User.role == UserRole.CUSTOMER)
    )
    handyman_count = await db.execute(
        select(func.count(User.id)).where(User.role == UserRole.HANDYMAN)
    )
    
    # Handyman verification stats
    verified_handymen = await db.execute(
        select(func.count(HandymanProfile.id))
        .where(HandymanProfile.verification_status == VerificationStatus.APPROVED)
    )
    pending_verifications = await db.execute(
        select(func.count(VerificationDocument.id))
        .where(VerificationDocument.status == VerificationStatus.PENDING)
    )
    
    # Job stats
    total_jobs = await db.execute(select(func.count(JobRequest.id)))
    open_jobs = await db.execute(
        select(func.count(JobRequest.id))
        .where(JobRequest.status == JobRequest.status.OPEN)
    )
    
    # Order stats
    total_orders = await db.execute(select(func.count(Order.id)))
    completed_orders = await db.execute(
        select(func.count(Order.id))
        .where(Order.status == OrderStatus.COMPLETED)
    )
    
    # Revenue (simplified)
    total_revenue = await db.execute(
        select(func.sum(Payment.amount))
        .where(Payment.status.in_(["completed", "payout_ready", "payout_completed"]))
    )
    total_commission = await db.execute(
        select(func.sum(Payment.commission))
        .where(Payment.status.in_(["completed", "payout_ready", "payout_completed"]))
    )
    
    return {
        "users": {
            "total": user_count.scalar() or 0,
            "customers": customer_count.scalar() or 0,
            "handymen": handyman_count.scalar() or 0,
        },
        "handymen": {
            "verified": verified_handymen.scalar() or 0,
            "pending_verifications": pending_verifications.scalar() or 0,
        },
        "jobs": {
            "total": total_jobs.scalar() or 0,
            "open": open_jobs.scalar() or 0,
        },
        "orders": {
            "total": total_orders.scalar() or 0,
            "completed": completed_orders.scalar() or 0,
        },
        "revenue": {
            "total": float(total_revenue.scalar() or 0),
            "commission": float(total_commission.scalar() or 0),
        },
    }


# ============ User Management ============

@router.get("/users")
async def list_users(
    role: Optional[UserRole] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """List all users with optional role filter."""
    query = select(User)
    
    if role:
        query = query.where(User.role == role)
    
    query = query.order_by(User.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    return {"items": users, "page": page, "page_size": page_size}


@router.patch("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Deactivate a user account."""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = False
    await db.commit()
    
    return {"message": "User deactivated successfully"}


@router.patch("/users/{user_id}/activate")
async def activate_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Activate a user account."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = True
    await db.commit()
    
    return {"message": "User activated successfully"}
