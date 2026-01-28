"""Reviews API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User, UserRole
from app.models.order import Order, OrderStatus
from app.models.handyman import HandymanProfile
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewResponse, ReviewListResponse, ReviewSummary

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_data: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a review after order completion."""
    # Get order
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.offer), selectinload(Order.job_request))
        .where(Order.id == review_data.order_id)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.status != OrderStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Can only review completed orders")
    
    # Determine participants
    from app.models.customer import CustomerProfile
    
    customer_result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.id == order.job_request.customer_id)
    )
    customer = customer_result.scalar_one()
    
    handyman_result = await db.execute(
        select(HandymanProfile).where(HandymanProfile.id == order.offer.handyman_id)
    )
    handyman = handyman_result.scalar_one()
    
    customer_user_id = customer.user_id
    handyman_user_id = handyman.user_id
    
    # Verify current user is a participant
    if current_user.id not in [customer_user_id, handyman_user_id]:
        raise HTTPException(status_code=403, detail="Not a participant in this order")
    
    # Verify to_user_id is the other participant
    if review_data.to_user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot review yourself")
    
    if review_data.to_user_id not in [customer_user_id, handyman_user_id]:
        raise HTTPException(status_code=400, detail="Invalid recipient")
    
    # Check if already reviewed
    existing = await db.execute(
        select(Review).where(
            and_(
                Review.order_id == review_data.order_id,
                Review.from_user_id == current_user.id,
            )
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already reviewed this order")
    
    # Create review
    review = Review(
        order_id=review_data.order_id,
        from_user_id=current_user.id,
        to_user_id=review_data.to_user_id,
        stars=review_data.stars,
        text=review_data.text,
    )
    db.add(review)
    
    # Update handyman rating if reviewing handyman
    if review_data.to_user_id == handyman_user_id:
        # Recalculate average rating
        rating_result = await db.execute(
            select(func.avg(Review.stars), func.count(Review.id))
            .where(Review.to_user_id == handyman_user_id)
        )
        avg_rating, total_reviews = rating_result.one()
        
        # Include new review in calculation
        new_avg = ((avg_rating or 0) * (total_reviews or 0) + review_data.stars) / ((total_reviews or 0) + 1)
        
        handyman.average_rating = new_avg
        handyman.total_reviews = (total_reviews or 0) + 1
    
    await db.commit()
    await db.refresh(review)
    
    return review


@router.get("/user/{user_id}", response_model=ReviewListResponse)
async def get_user_reviews(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get reviews for a user (public endpoint)."""
    result = await db.execute(
        select(Review)
        .options(selectinload(Review.from_user))
        .where(Review.to_user_id == user_id)
        .order_by(Review.created_at.desc())
    )
    reviews = result.scalars().all()
    
    # Calculate average
    if reviews:
        avg_rating = sum(r.stars for r in reviews) / len(reviews)
    else:
        avg_rating = 0.0
    
    # Add reviewer names
    review_responses = []
    for review in reviews:
        resp = ReviewResponse.model_validate(review)
        resp.from_user_name = review.from_user.name if review.from_user else None
        review_responses.append(resp)
    
    return ReviewListResponse(
        items=review_responses,
        total=len(reviews),
        average_rating=avg_rating,
    )


@router.get("/user/{user_id}/summary", response_model=ReviewSummary)
async def get_user_review_summary(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get review summary for a user."""
    result = await db.execute(
        select(Review).where(Review.to_user_id == user_id)
    )
    reviews = result.scalars().all()
    
    if not reviews:
        return ReviewSummary(
            average_rating=0.0,
            total_reviews=0,
            rating_distribution={1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
        )
    
    # Calculate distribution
    distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for review in reviews:
        distribution[review.stars] += 1
    
    avg_rating = sum(r.stars for r in reviews) / len(reviews)
    
    return ReviewSummary(
        average_rating=avg_rating,
        total_reviews=len(reviews),
        rating_distribution=distribution,
    )
