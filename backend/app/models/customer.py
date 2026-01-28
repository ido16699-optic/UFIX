"""Customer profile model."""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CustomerProfile(Base):
    """Customer profile with addresses and preferences."""
    __tablename__ = "customer_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    
    # Address information
    default_address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    default_latitude: Mapped[Optional[float]] = mapped_column(nullable=True)
    default_longitude: Mapped[Optional[float]] = mapped_column(nullable=True)
    
    # Saved addresses as JSON array
    saved_addresses: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=list)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="customer_profile")
    job_requests: Mapped[List["JobRequest"]] = relationship("JobRequest", back_populates="customer")
