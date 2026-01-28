"""Order and payment models."""
import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Float, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.config import settings


class OrderStatus(str, enum.Enum):
    """Status of an order/job."""
    PENDING_PAYMENT = "pending_payment"
    PAYMENT_AUTHORIZED = "payment_authorized"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"


class PaymentStatus(str, enum.Enum):
    """Status of a payment."""
    PENDING = "pending"
    AUTHORIZED = "authorized"  # Card charged, funds held
    COMPLETED = "completed"  # Payment finalized
    PAYOUT_READY = "payout_ready"  # Ready to pay handyman
    PAYOUT_COMPLETED = "payout_completed"
    REFUNDED = "refunded"
    FAILED = "failed"


class Order(Base):
    """Order created when an offer is accepted."""
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    job_request_id: Mapped[int] = mapped_column(ForeignKey("job_requests.id"), nullable=False)
    offer_id: Mapped[int] = mapped_column(ForeignKey("offers.id"), nullable=False)
    
    # Status
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus), default=OrderStatus.PENDING_PAYMENT
    )
    
    # Timestamps
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    job_request: Mapped["JobRequest"] = relationship("JobRequest", back_populates="order")
    offer: Mapped["Offer"] = relationship("Offer", back_populates="order")
    payment: Mapped[Optional["Payment"]] = relationship("Payment", back_populates="order", uselist=False)
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="order")


class Payment(Base):
    """Payment record for an order."""
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), unique=True, nullable=False)
    
    # Payment details
    provider: Mapped[str] = mapped_column(String(50), default="stripe")
    provider_payment_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Stripe payment intent ID
    provider_charge_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Amounts (in cents)
    amount: Mapped[float] = mapped_column(Float, nullable=False)  # Total charged
    commission: Mapped[float] = mapped_column(Float, nullable=False)  # Platform commission
    handyman_payout: Mapped[float] = mapped_column(Float, nullable=False)  # Amount to handyman
    
    # Status
    status: Mapped[PaymentStatus] = mapped_column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    
    # Payout tracking
    payout_reference: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    payout_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="payment")
    
    @staticmethod
    def calculate_commission(amount: float) -> tuple[float, float]:
        """Calculate commission and handyman payout.
        
        Returns:
            tuple: (commission_amount, handyman_payout)
        """
        commission = amount * settings.PLATFORM_COMMISSION_RATE
        handyman_payout = amount - commission
        return commission, handyman_payout
