"""Job request and offer models."""
import enum
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, DateTime, ForeignKey, Float, Enum, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.handyman import ServiceCategory


class RequestType(str, enum.Enum):
    """Job request type - ASAP or scheduled."""
    ASAP = "asap"
    SCHEDULED = "scheduled"


class JobRequestStatus(str, enum.Enum):
    """Status of a job request."""
    OPEN = "open"  # Accepting offers
    MATCHED = "matched"  # Offer accepted, waiting for payment
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class OfferStatus(str, enum.Enum):
    """Status of an offer."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"
    WITHDRAWN = "withdrawn"


class JobRequest(Base):
    """Job request created by customer."""
    __tablename__ = "job_requests"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer_profiles.id"), nullable=False)
    
    # Job details
    category: Mapped[ServiceCategory] = mapped_column(Enum(ServiceCategory), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Location
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Scheduling
    request_type: Mapped[RequestType] = mapped_column(Enum(RequestType), nullable=False)
    scheduled_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    scheduled_time_window: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # e.g., "9:00-12:00"
    
    # Status
    status: Mapped[JobRequestStatus] = mapped_column(
        Enum(JobRequestStatus), default=JobRequestStatus.OPEN
    )
    
    # Optional: images of the problem
    images: Mapped[Optional[dict]] = mapped_column(type_=None, nullable=True)  # JSON array of URLs
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer: Mapped["CustomerProfile"] = relationship("CustomerProfile", back_populates="job_requests")
    offers: Mapped[List["Offer"]] = relationship("Offer", back_populates="job_request")
    order: Mapped[Optional["Order"]] = relationship("Order", back_populates="job_request", uselist=False)
    chat_thread: Mapped[Optional["ChatThread"]] = relationship("ChatThread", back_populates="job_request", uselist=False)


class Offer(Base):
    """Offer from handyman for a job request."""
    __tablename__ = "offers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    job_request_id: Mapped[int] = mapped_column(ForeignKey("job_requests.id"), nullable=False)
    handyman_id: Mapped[int] = mapped_column(ForeignKey("handyman_profiles.id"), nullable=False)
    
    # Offer details
    price: Mapped[float] = mapped_column(Float, nullable=False)  # Price in cents/smallest currency unit
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Availability/ETA
    estimated_arrival_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # For ASAP
    available_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)  # For scheduled
    available_time_window: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Status
    status: Mapped[OfferStatus] = mapped_column(Enum(OfferStatus), default=OfferStatus.PENDING)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    job_request: Mapped["JobRequest"] = relationship("JobRequest", back_populates="offers")
    handyman: Mapped["HandymanProfile"] = relationship("HandymanProfile", back_populates="offers")
    order: Mapped[Optional["Order"]] = relationship("Order", back_populates="offer", uselist=False)
