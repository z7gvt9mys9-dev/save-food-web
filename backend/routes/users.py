"""User profile and management routes"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import crud
from models import UserResponse, UserUpdate
from database import get_db
from routes.auth import get_current_user
from auth import verify_password

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user = Depends(get_current_user)):
    """Get current user's profile"""
    return UserResponse.from_orm(current_user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    user = crud.get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.from_orm(user)


@router.put("/me", response_model=UserResponse)
async def update_profile(
    user_update: UserUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile"""
    # If password is being changed, require old password verification
    if user_update.password:
        if not user_update.old_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Old password required to change password"
            )
        if not verify_password(user_update.old_password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect current password"
            )
    
    updated_user = crud.update_user(
        db,
        current_user.id,
        name=user_update.name,
        avatar=user_update.avatar,
        password=user_update.password
    )
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update profile"
        )
    
    return UserResponse.from_orm(updated_user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user_profile(
    user_id: int,
    user_update: UserUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile by ID (user or admin only)"""
    # Check if the user is updating their own profile or is admin
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile"
        )
    
    updated_user = crud.update_user(
        db,
        user_id,
        name=user_update.name,
        avatar=user_update.avatar,
        password=user_update.password
    )
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update profile"
        )
    
    return UserResponse.from_orm(updated_user)


@router.get("/{user_id}/stats")
async def get_user_stats(user_id: int, db: Session = Depends(get_db)):
    """Get user statistics and gamification info"""
    user = crud.get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "user_id": user.id,
        "name": user.name,
        "xp": user.xp,
        "rating_level": user.rating_level,
        "is_admin": user.is_admin,
        "total_donations": len(user.donations),
        "total_issues_created": len(user.issues_created),
        "total_issues_assigned": len(user.issues_assigned),
        "total_closed_issues": len([i for i in user.issues_assigned if i.status == "closed"])
    }

