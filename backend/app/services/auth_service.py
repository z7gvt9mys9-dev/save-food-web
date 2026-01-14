"""
Authentication service
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import get_settings
from app.utils.errors import AuthenticationError, NotFoundError
from crud import get_user_by_email


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Authentication business logic"""
    
    def __init__(self):
        self.settings = get_settings()
    
    def hash_password(self, password: str) -> str:
        """Hash password"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, user_id: int) -> tuple[str, datetime]:
        """Create JWT access token"""
        expires_at = datetime.utcnow() + timedelta(
            minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        
        data = {
            "sub": str(user_id),
            "exp": expires_at,
        }
        
        encoded_jwt = jwt.encode(
            data,
            self.settings.SECRET_KEY,
            algorithm=self.settings.ALGORITHM,
        )
        
        return encoded_jwt, expires_at
    
    def verify_token(self, token: str) -> int:
        """Verify and decode JWT token, return user_id"""
        try:
            payload = jwt.decode(
                token,
                self.settings.SECRET_KEY,
                algorithms=[self.settings.ALGORITHM],
            )
            user_id: str = payload.get("sub")
            
            if user_id is None:
                raise AuthenticationError("Invalid token")
            
            return int(user_id)
        
        except JWTError:
            raise AuthenticationError("Invalid or expired token")
    
    def authenticate_user(
        self, db: Session, email: str, password: str
    ) -> tuple[int, str]:
        """Authenticate user by email and password"""
        user = get_user_by_email(db, email)
        
        if not user or not self.verify_password(password, user.password):
            raise AuthenticationError("Invalid email or password")
        
        token, _ = self.create_access_token(user.id)
        return user.id, token


# Singleton instance
auth_service = AuthService()
