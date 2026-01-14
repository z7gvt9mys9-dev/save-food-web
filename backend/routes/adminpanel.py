"""Admin panel routes for user management and system administration"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import crud
from models import UserResponse, UserDB
from database import get_db
from routes.auth import get_current_user

router = APIRouter(prefix="/api/admin", tags=["admin"])


def check_admin_access(current_user = Depends(get_current_user)):
    """Check if current user has admin privileges"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def check_developer_access(current_user = Depends(get_current_user)):
    """Check if current user is Developer"""
    if current_user.name != "Developer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Developer can perform this action"
        )
    return current_user


@router.get("/admins", response_model=List[UserResponse])
async def get_admins(
    current_user = Depends(check_admin_access),
    db: Session = Depends(get_db)
):
    """Get all admin users"""
    admins = db.query(UserDB).filter(UserDB.is_admin == True).all()
    return [UserResponse.from_orm(admin) for admin in admins]


@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    current_user = Depends(check_admin_access),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)"""
    users = db.query(UserDB).all()
    return [UserResponse.from_orm(user) for user in users]


@router.post("/users/{user_id}/ban")
async def ban_user(
    user_id: int,
    reason: str = "No reason provided",
    current_user = Depends(check_admin_access),
    db: Session = Depends(get_db)
):
    """Ban a user"""
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_banned:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already banned"
        )
    
    user.is_banned = True
    db.commit()
    db.refresh(user)
    
    return {
        "message": f"User {user.name} has been banned",
        "user": UserResponse.from_orm(user)
    }


@router.delete("/users/{user_id}/ban")
async def unban_user(
    user_id: int,
    current_user = Depends(check_admin_access),
    db: Session = Depends(get_db)
):
    """Unban a user"""
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_banned:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not banned"
        )
    
    user.is_banned = False
    db.commit()
    db.refresh(user)
    
    return {
        "message": f"User {user.name} has been unbanned",
        "user": UserResponse.from_orm(user)
    }


@router.get("/users/{user_id}/ban-status")
async def get_ban_status(
    user_id: int,
    current_user = Depends(check_admin_access),
    db: Session = Depends(get_db)
):
    """Get ban status of a user"""
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "user_id": user.id,
        "is_banned": user.is_banned
    }


@router.get("/users/banned/list", response_model=List[UserResponse])
async def get_banned_users(
    current_user = Depends(check_admin_access),
    db: Session = Depends(get_db)
):
    """Get list of all banned users"""
    banned_users = db.query(UserDB).filter(UserDB.is_banned == True).all()
    return [UserResponse.from_orm(user) for user in banned_users]


@router.post("/users/{user_id}/promote")
async def promote_to_admin(
    user_id: int,
    current_user = Depends(check_developer_access),
    db: Session = Depends(get_db)
):
    """Promote user to admin (Developer only)"""
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already an admin"
        )
    
    user.is_admin = True
    db.commit()
    db.refresh(user)
    
    return {
        "message": f"User {user.name} has been promoted to admin",
        "user": UserResponse.from_orm(user)
    }


@router.post("/users/{user_id}/demote")
async def demote_from_admin(
    user_id: int,
    current_user = Depends(check_developer_access),
    db: Session = Depends(get_db)
):
    """Demote admin to regular user (Developer only)"""
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not an admin"
        )
    
    # Prevent demoting Developer
    if user.name == "Developer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot demote Developer"
        )
    
    user.is_admin = False
    db.commit()
    db.refresh(user)
    
    return {
        "message": f"User {user.name} has been demoted from admin",
        "user": UserResponse.from_orm(user)
    }
    
    