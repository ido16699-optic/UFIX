"""Pydantic schemas for Reviews."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ============ Review Schemas ============

class ReviewCreate(BaseModel):
    """Schema for creating a review."""
    order_id: int
    to_user_id: int
    stars: int = Field(..., ge=1, le=5)
    text: Optional[str] = Field(None, max_length=1000)


class ReviewResponse(BaseModel):
    """Review response."""
    id: int
    order_id: int
    from_user_id: int
    to_user_id: int
    stars: int
    text: Optional[str] = None
    created_at: datetime
    from_user_name: Optional[str] = None  # Computed
    to_user_name: Optional[str] = None  # Computed

    class Config:
        from_attributes = True


class ReviewListResponse(BaseModel):
    """List of reviews."""
    items: List[ReviewResponse]
    total: int
    average_rating: float


class ReviewSummary(BaseModel):
    """Review summary for a user."""
    average_rating: float
    total_reviews: int
    rating_distribution: dict  # {1: count, 2: count, ...}
