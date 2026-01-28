"""Pydantic schemas for Job requests and offers."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from app.models.handyman import ServiceCategory
from app.models.job import RequestType, JobRequestStatus, OfferStatus
from app.schemas.handyman import HandymanPublicProfile


# ============ Job Request Schemas ============

class JobRequestCreate(BaseModel):
    """Schema for creating a job request."""
    category: ServiceCategory
    title: str = Field(..., min_length=5, max_length=255)
    description: str = Field(..., min_length=10, max_length=2000)
    address: str = Field(..., max_length=500)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    request_type: RequestType
    scheduled_date: Optional[datetime] = None  # Required if request_type is SCHEDULED
    scheduled_time_window: Optional[str] = Field(None, max_length=100)
    images: Optional[List[str]] = None  # URLs of uploaded images


class JobRequestUpdate(BaseModel):
    """Schema for updating a job request."""
    title: Optional[str] = Field(None, min_length=5, max_length=255)
    description: Optional[str] = Field(None, min_length=10, max_length=2000)
    address: Optional[str] = Field(None, max_length=500)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    scheduled_date: Optional[datetime] = None
    scheduled_time_window: Optional[str] = Field(None, max_length=100)


class JobRequestResponse(BaseModel):
    """Job request response."""
    id: int
    customer_id: int
    category: ServiceCategory
    title: str
    description: str
    address: str
    latitude: float
    longitude: float
    request_type: RequestType
    scheduled_date: Optional[datetime] = None
    scheduled_time_window: Optional[str] = None
    status: JobRequestStatus
    images: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime
    offer_count: Optional[int] = None  # Computed field

    class Config:
        from_attributes = True


class JobRequestListResponse(BaseModel):
    """List of job requests with pagination."""
    items: List[JobRequestResponse]
    total: int
    page: int
    page_size: int


# ============ Offer Schemas ============

class OfferCreate(BaseModel):
    """Schema for creating an offer."""
    job_request_id: int
    price: float = Field(..., gt=0)  # Price in currency units
    message: Optional[str] = Field(None, max_length=500)
    estimated_arrival_minutes: Optional[int] = Field(None, ge=1)  # For ASAP requests
    available_date: Optional[datetime] = None  # For scheduled requests
    available_time_window: Optional[str] = Field(None, max_length=100)


class OfferResponse(BaseModel):
    """Offer response."""
    id: int
    job_request_id: int
    handyman_id: int
    price: float
    message: Optional[str] = None
    estimated_arrival_minutes: Optional[int] = None
    available_date: Optional[datetime] = None
    available_time_window: Optional[str] = None
    status: OfferStatus
    created_at: datetime
    handyman: Optional[HandymanPublicProfile] = None

    class Config:
        from_attributes = True


class OfferListResponse(BaseModel):
    """List of offers for a job request."""
    items: List[OfferResponse]
    total: int


class OfferAccept(BaseModel):
    """Schema for accepting an offer."""
    offer_id: int
