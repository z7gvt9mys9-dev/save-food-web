"""Admin panel data models and schemas"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AdminListResponse(BaseModel):
    """Admin user response - only email and name"""
    id: int
    email: str
    name: str
    
    class Config:
        from_attributes = True


class BanRequest(BaseModel):
    """Ban user request"""
    reason: Optional[str] = None


class BanResponse(BaseModel):
    """Ban response"""
    user_id: int
    is_banned: bool
    message: str


class UnbanResponse(BaseModel):
    """Unban response"""
    user_id: int
    is_banned: bool
    message: str


class BanStatusResponse(BaseModel):
    """Ban status response"""
    user_id: int
    email: str
    is_banned: bool
    name: str
