"""Handyman profile and verification models."""
import enum
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, DateTime, ForeignKey, Float, Integer, Enum, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ServiceCategory(str, enum.Enum):
    """Fixed service categories for MVP."""
    PLUMBING = "plumbing"
    ELECTRICAL = "electrical"
    PAINTING = "painting"
    FURNITURE_ASSEMBLY = "furniture_assembly"
    GENERAL_HANDYMAN = "general_handyman"


class VerificationStatus(str, enum.Enum):
    """Handyman verification status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class HandymanProfile(Base):
    """Handyman profile with services, verification, and ratings."""
    __tablename__ = "handyman_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    
    # Service info
    categories: Mapped[dict] = mapped_column(JSON, nullable=False, default=list)  # List of ServiceCategory values
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    service_radius_km: Mapped[float] = mapped_column(Float, default=10.0)
    
    # Location (for matching nearby jobs)
    current_latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    current_longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Verification
    verification_status: Mapped[VerificationStatus] = mapped_column(
        Enum(VerificationStatus), default=VerificationStatus.PENDING
    )
    
    # Rating stats (denormalized for performance)
    average_rating: Mapped[float] = mapped_column(Float, default=0.0)
    total_reviews: Mapped[int] = mapped_column(Integer, default=0)
    total_completed_jobs: Mapped[int] = mapped_column(Integer, default=0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="handyman_profile")
    verification_documents: Mapped[List["VerificationDocument"]] = relationship(
        "VerificationDocument", back_populates="handyman"
    )
    offers: Mapped[List["Offer"]] = relationship("Offer", back_populates="handyman")


class VerificationDocument(Base):
    """Documents uploaded by handyman for verification."""
    __tablename__ = "verification_documents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    handyman_id: Mapped[int] = mapped_column(ForeignKey("handyman_profiles.id"), nullable=False)
    
    # File storage
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., "id_card", "license"
    
    # Review status
    status: Mapped[VerificationStatus] = mapped_column(
        Enum(VerificationStatus), default=VerificationStatus.PENDING
    )
    reviewed_by_admin_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    review_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    handyman: Mapped["HandymanProfile"] = relationship("HandymanProfile", back_populates="verification_documents")
