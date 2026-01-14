"""Authentication routes for user login, registration, and token management"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from typing import Optional
from sqlalchemy.orm import Session
from auth import create_access_token, verify_token, verify_password
import crud
from models import UserCreate, UserResponse, LoginRequest, AuthResponse
from database import get_db

router = APIRouter(prefix="/api/auth", tags=["auth"])


def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Dependency to get current authenticated user"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    # Extract token from Bearer <token>
    parts = authorization.split()
    if len(parts) != 2 or parts[0] != "Bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header"
        )
    
    token = parts[1]
    
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token payload"
        )
    
    user = crud.get_user_by_id(db, int(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.post("/register", response_model=AuthResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if email already exists
    existing_user = crud.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    db_user = crud.create_user(
        db,
        email=user_data.email,
        name=user_data.name,
        password=user_data.password,
        role=user_data.role
    )
    
    # Generate token
    access_token = create_access_token(data={"sub": str(db_user.id)})
    
    return {
        "token": access_token,
        "user": UserResponse.from_orm(db_user)
    }


@router.post("/login", response_model=AuthResponse)
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """Login with email and password"""
    user = crud.get_user_by_email(db, credentials.email)
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Generate token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {
        "token": access_token,
        "user": UserResponse.from_orm(user)
    }


@router.get("/verify")
async def verify_token_endpoint(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify if current user token is valid"""
    return {
        "valid": True,
        "user": UserResponse.from_orm(current_user)
    }
