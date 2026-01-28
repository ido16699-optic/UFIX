"""User model and related enums."""
import enum
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Enum, DateTime, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserRole(str, enum.Enum):
    """User roles in the system."""
    CUSTOMER = "customer"
    HANDYMAN = "handyman"
    ADMIN = "admin"


class User(Base):
    """User model - base entity for all users."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer_profile: Mapped[Optional["CustomerProfile"]] = relationship(
        "CustomerProfile", back_populates="user", uselist=False
    )
    handyman_profile: Mapped[Optional["HandymanProfile"]] = relationship(
        "HandymanProfile", back_populates="user", uselist=False
    )
    
    # Reviews given by this user
    reviews_given: Mapped[List["Review"]] = relationship(
        "Review", foreign_keys="Review.from_user_id", back_populates="from_user"
    )
    # Reviews received by this user
    reviews_received: Mapped[List["Review"]] = relationship(
        "Review", foreign_keys="Review.to_user_id", back_populates="to_user"
    )
