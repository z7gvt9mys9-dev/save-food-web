"""
Pydantic models for API responses and requests
"""

from typing import Optional, Any, Generic, TypeVar
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    """Standard success response"""
    status: str = "success"
    data: T
    message: Optional[str] = None


class ErrorDetail(BaseModel):
    """Error detail"""
    field: Optional[str] = None
    message: str


class ErrorResponse(BaseModel):
    """Standard error response"""
    status: str = "error"
    type: str
    message: str
    details: Optional[dict[str, Any]] = None


# Auth Models
class LoginRequest(BaseModel):
    """Login request"""
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=6, max_length=128)
    
    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format"""
        if "@" not in v or "." not in v:
            raise ValueError("Invalid email format")
        return v.lower().strip()


class RegisterRequest(BaseModel):
    """Register request"""
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=6, max_length=128)
    full_name: str = Field(..., min_length=2, max_length=100)
    role: str = Field(..., pattern="^(donor|deliverer|receiver)$")
    
    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format"""
        if "@" not in v or "." not in v:
            raise ValueError("Invalid email format")
        return v.lower().strip()


class AuthResponse(BaseModel):
    """Authentication response"""
    id: int
    email: str
    full_name: str
    role: str
    access_token: str
    token_type: str = "bearer"


# User Models
class UserResponse(BaseModel):
    """User response model"""
    id: int
    email: str
    full_name: str
    role: str
    avatar: Optional[str] = None
    rating_level: int = 0
    xp: int = 0
    created_at: datetime
    
    class Config:
        from_attributes = True


class UpdateUserRequest(BaseModel):
    """Update user request"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    avatar: Optional[str] = None
    
    @field_validator("full_name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate name"""
        if v is not None:
            return v.strip()
        return v


class UserStatsResponse(BaseModel):
    """User statistics"""
    user_id: int
    donations_completed: int = 0
    deliveries_completed: int = 0
    items_received: int = 0
    rating_level: int = 0
    xp: int = 0


# Project Models
class CreateProjectRequest(BaseModel):
    """Create project request"""
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10, max_length=1000)
    image_url: Optional[str] = None
    category: str = Field(..., pattern="^(food|clothing|other)$")


class UpdateProjectRequest(BaseModel):
    """Update project request"""
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, min_length=10, max_length=1000)
    image_url: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(active|completed|cancelled)$")


class ProjectResponse(BaseModel):
    """Project response model"""
    id: int
    title: str
    description: str
    image_url: Optional[str] = None
    category: str
    status: str
    created_by: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Notification Models
class NotificationResponse(BaseModel):
    """Notification response"""
    id: int
    user_id: int
    title: str
    message: str
    type: str
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class CreateNotificationRequest(BaseModel):
    """Create notification request"""
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=1000)
    type: str = Field(..., pattern="^(info|success|warning|error)$")
