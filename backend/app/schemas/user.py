"""Pydantic schemas for User authentication and profiles."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator

from app.models.user import UserRole


# ============ Auth Schemas ============

class UserRegister(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    name: str = Field(..., min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    role: UserRole  # customer or handyman


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """JWT token payload."""
    sub: int  # user_id
    role: UserRole
    exp: datetime


# ============ User Schemas ============

class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    name: str
    phone: Optional[str] = None
    role: UserRole


class UserResponse(UserBase):
    """User response schema."""
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schema for updating user info."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)


# ============ Customer Profile Schemas ============

class AddressSchema(BaseModel):
    """Address schema for saved addresses."""
    label: str = Field(..., max_length=100)  # e.g., "Home", "Office"
    address: str = Field(..., max_length=500)
    latitude: float
    longitude: float


class CustomerProfileBase(BaseModel):
    """Base customer profile schema."""
    default_address: Optional[str] = None
    default_latitude: Optional[float] = None
    default_longitude: Optional[float] = None
    saved_addresses: Optional[List[AddressSchema]] = []


class CustomerProfileCreate(CustomerProfileBase):
    """Schema for creating customer profile."""
    pass


class CustomerProfileUpdate(BaseModel):
    """Schema for updating customer profile."""
    default_address: Optional[str] = None
    default_latitude: Optional[float] = None
    default_longitude: Optional[float] = None
    saved_addresses: Optional[List[AddressSchema]] = None


class CustomerProfileResponse(CustomerProfileBase):
    """Customer profile response."""
    id: int
    user_id: int
    created_at: datetime
    user: Optional[UserResponse] = None

    class Config:
        from_attributes = True
