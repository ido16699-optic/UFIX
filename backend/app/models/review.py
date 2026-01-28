"""Review model for ratings and reviews."""
from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, Integer, Text, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Review(Base):
    """Review/rating between customer and handyman after job completion."""
    __tablename__ = "reviews"
    
    __table_args__ = (
        CheckConstraint('stars >= 1 AND stars <= 5', name='valid_star_rating'),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    
    # Who wrote the review
    from_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    # Who is being reviewed
    to_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # Review content
    stars: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5
    text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="reviews")
    from_user: Mapped["User"] = relationship("User", foreign_keys=[from_user_id], back_populates="reviews_given")
    to_user: Mapped["User"] = relationship("User", foreign_keys=[to_user_id], back_populates="reviews_received")
