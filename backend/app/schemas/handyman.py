"""Pydantic schemas for Handyman profiles and verification."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from app.models.handyman import ServiceCategory, VerificationStatus
from app.schemas.user import UserResponse


# ============ Handyman Profile Schemas ============

class HandymanProfileBase(BaseModel):
    """Base handyman profile schema."""
    categories: List[ServiceCategory] = Field(..., min_length=1)
    bio: Optional[str] = Field(None, max_length=1000)
    service_radius_km: float = Field(default=10.0, ge=1.0, le=100.0)


class HandymanProfileCreate(HandymanProfileBase):
    """Schema for creating handyman profile."""
    pass


class HandymanProfileUpdate(BaseModel):
    """Schema for updating handyman profile."""
    categories: Optional[List[ServiceCategory]] = None
    bio: Optional[str] = Field(None, max_length=1000)
    service_radius_km: Optional[float] = Field(None, ge=1.0, le=100.0)
    current_latitude: Optional[float] = None
    current_longitude: Optional[float] = None


class HandymanProfileResponse(HandymanProfileBase):
    """Handyman profile response."""
    id: int
    user_id: int
    current_latitude: Optional[float] = None
    current_longitude: Optional[float] = None
    verification_status: VerificationStatus
    average_rating: float
    total_reviews: int
    total_completed_jobs: int
    created_at: datetime
    user: Optional[UserResponse] = None

    class Config:
        from_attributes = True


class HandymanPublicProfile(BaseModel):
    """Public handyman profile (for customers)."""
    id: int
    user_id: int
    name: str  # From user
    categories: List[ServiceCategory]
    bio: Optional[str]
    verification_status: VerificationStatus
    average_rating: float
    total_reviews: int
    total_completed_jobs: int

    class Config:
        from_attributes = True


# ============ Verification Document Schemas ============

class VerificationDocumentCreate(BaseModel):
    """Schema for uploading verification document."""
    file_type: str = Field(..., max_length=50)  # e.g., "id_card", "license"


class VerificationDocumentResponse(BaseModel):
    """Verification document response."""
    id: int
    handyman_id: int
    file_url: str
    file_type: str
    status: VerificationStatus
    reviewed_by_admin_id: Optional[int] = None
    review_notes: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class VerificationReview(BaseModel):
    """Admin schema for reviewing verification."""
    status: VerificationStatus
    review_notes: Optional[str] = Field(None, max_length=500)


# ============ Location Update ============

class LocationUpdate(BaseModel):
    """Schema for updating handyman location."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
