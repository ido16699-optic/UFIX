"""Profile management API endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_customer, get_current_handyman
from app.models.user import User, UserRole
from app.models.customer import CustomerProfile
from app.models.handyman import HandymanProfile, VerificationDocument, VerificationStatus
from app.schemas.user import (
    UserResponse,
    UserUpdate,
    CustomerProfileResponse,
    CustomerProfileUpdate,
)
from app.schemas.handyman import (
    HandymanProfileResponse,
    HandymanProfileUpdate,
    HandymanPublicProfile,
    VerificationDocumentCreate,
    VerificationDocumentResponse,
    LocationUpdate,
)

router = APIRouter(prefix="/profiles", tags=["Profiles"])


# ============ Customer Profile ============

@router.get("/customer/me", response_model=CustomerProfileResponse)
async def get_my_customer_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_customer),
):
    """Get current customer's profile."""
    result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return profile


@router.patch("/customer/me", response_model=CustomerProfileResponse)
async def update_my_customer_profile(
    profile_data: CustomerProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_customer),
):
    """Update current customer's profile."""
    result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Update fields
    update_data = profile_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    await db.commit()
    await db.refresh(profile)
    
    return profile


# ============ Handyman Profile ============

@router.get("/handyman/me", response_model=HandymanProfileResponse)
async def get_my_handyman_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_handyman),
):
    """Get current handyman's profile."""
    result = await db.execute(
        select(HandymanProfile).where(HandymanProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return profile


@router.patch("/handyman/me", response_model=HandymanProfileResponse)
async def update_my_handyman_profile(
    profile_data: HandymanProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_handyman),
):
    """Update current handyman's profile."""
    result = await db.execute(
        select(HandymanProfile).where(HandymanProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Update fields
    update_data = profile_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    await db.commit()
    await db.refresh(profile)
    
    return profile


@router.post("/handyman/me/location", response_model=HandymanProfileResponse)
async def update_handyman_location(
    location: LocationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_handyman),
):
    """Update handyman's current location."""
    result = await db.execute(
        select(HandymanProfile).where(HandymanProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    profile.current_latitude = location.latitude
    profile.current_longitude = location.longitude
    
    await db.commit()
    await db.refresh(profile)
    
    return profile


# ============ Verification Documents ============

@router.post("/handyman/me/verification", response_model=VerificationDocumentResponse)
async def upload_verification_document(
    file_type: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_handyman),
):
    """Upload a verification document (ID card, license, etc.)."""
    result = await db.execute(
        select(HandymanProfile).where(HandymanProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # For MVP, we'll save file info without actual S3 upload
    # In production, upload to S3 and get URL
    file_url = f"/uploads/verification/{current_user.id}/{file.filename}"
    
    # TODO: Implement actual S3 upload
    # import boto3
    # s3_client = boto3.client('s3', ...)
    # s3_client.upload_fileobj(file.file, bucket, key)
    # file_url = f"https://{bucket}.s3.amazonaws.com/{key}"
    
    document = VerificationDocument(
        handyman_id=profile.id,
        file_url=file_url,
        file_type=file_type,
        status=VerificationStatus.PENDING,
    )
    db.add(document)
    
    # Set profile to pending if not already approved
    if profile.verification_status != VerificationStatus.APPROVED:
        profile.verification_status = VerificationStatus.PENDING
    
    await db.commit()
    await db.refresh(document)
    
    return document


@router.get("/handyman/me/verification", response_model=list[VerificationDocumentResponse])
async def get_my_verification_documents(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_handyman),
):
    """Get handyman's verification documents."""
    result = await db.execute(
        select(HandymanProfile).where(HandymanProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    doc_result = await db.execute(
        select(VerificationDocument)
        .where(VerificationDocument.handyman_id == profile.id)
        .order_by(VerificationDocument.created_at.desc())
    )
    documents = doc_result.scalars().all()
    
    return documents


# ============ Public Handyman Profile ============

@router.get("/handyman/{handyman_id}", response_model=HandymanPublicProfile)
async def get_handyman_public_profile(
    handyman_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get public handyman profile (for customers viewing offers)."""
    from sqlalchemy.orm import selectinload
    
    result = await db.execute(
        select(HandymanProfile)
        .options(selectinload(HandymanProfile.user))
        .where(HandymanProfile.id == handyman_id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Handyman not found")
    
    return HandymanPublicProfile(
        id=profile.id,
        user_id=profile.user_id,
        name=profile.user.name,
        categories=profile.categories,
        bio=profile.bio,
        verification_status=profile.verification_status,
        average_rating=profile.average_rating,
        total_reviews=profile.total_reviews,
        total_completed_jobs=profile.total_completed_jobs,
    )
