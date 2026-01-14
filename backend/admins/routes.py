"""Admin panel API routes"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from routes.auth import get_current_user
from models import UserDB
from .models import AdminListResponse, BanRequest, BanResponse, UnbanResponse, BanStatusResponse
from .services import admin_service

router = APIRouter(prefix="/api/admin", tags=["admin"])


def check_admin(current_user: UserDB = Depends(get_current_user)) -> UserDB:
    """Dependency to verify admin privileges"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


@router.get("/admins", response_model=list[AdminListResponse])
async def get_all_admins(
    admin_user: UserDB = Depends(check_admin),
    db: Session = Depends(get_db)
):
    """Get list of all admin users (admin only)"""
    admins = admin_service.get_all_admins(db)
    return [
        AdminListResponse(id=a.id, email=a.email, name=a.name)
        for a in admins
    ]


@router.post("/users/{user_id}/ban", response_model=BanResponse)
async def ban_user(
    user_id: int,
    ban_req: BanRequest,
    admin_user: UserDB = Depends(check_admin),
    db: Session = Depends(get_db)
):
    """Ban a user (admin only)"""
    user = admin_service.ban_user(db, user_id, ban_req.reason)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="❌ User not found"
        )
    
    return BanResponse(
        user_id=user.id,
        is_banned=user.is_banned,
        message=f"User {user.email} has been banned"
    )


@router.delete("/users/{user_id}/ban", response_model=UnbanResponse)
async def unban_user(
    user_id: int,
    admin_user: UserDB = Depends(check_admin),
    db: Session = Depends(get_db)
):
    """Unban a user (admin only)"""
    user = admin_service.unban_user(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="❌ User not found"
        )
    
    return UnbanResponse(
        user_id=user.id,
        is_banned=user.is_banned,
        message=f"User {user.email} has been unbanned"
    )


@router.get("/users/{user_id}/ban-status", response_model=BanStatusResponse)
async def get_ban_status(
    user_id: int,
    admin_user: UserDB = Depends(check_admin),
    db: Session = Depends(get_db)
):
    """Check ban status of a user"""
    status_info = admin_service.get_user_ban_status(db, user_id)
    
    if not status_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="❌ User not found"
        )
    
    return BanStatusResponse(**status_info)


@router.get("/users/banned/list", response_model=list[BanStatusResponse])
async def get_banned_users_list(
    admin_user: UserDB = Depends(check_admin),
    db: Session = Depends(get_db)
):
    """Get list of all banned users"""
    banned_users = admin_service.get_all_banned_users(db)
    return [
        BanStatusResponse(
            user_id=u.id,
            email=u.email,
            name=u.name,
            is_banned=u.is_banned
        )
        for u in banned_users
    ]
