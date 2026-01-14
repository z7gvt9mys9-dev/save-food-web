"""User repository for database operations"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from models import UserDB
from .base_repository import BaseRepository
from typing import Optional, List


class UserRepository(BaseRepository[UserDB]):
    """Repository for User model"""
    
    def __init__(self):
        super().__init__(UserDB)
    
    def get_by_email(self, db: Session, email: str) -> Optional[UserDB]:
        """Get user by email"""
        return db.query(UserDB).filter(UserDB.email == email).first()
    
    def get_admins(self, db: Session) -> List[UserDB]:
        """Get all admin users"""
        return db.query(UserDB).filter(UserDB.is_admin == True).all()
    
    def ban_user(self, db: Session, user_id: int) -> Optional[UserDB]:
        """Ban user (soft delete with is_banned flag)"""
        user = self.get_by_id(db, user_id)
        if user:
            user.is_banned = True
            db.commit()
            db.refresh(user)
        return user
    
    def unban_user(self, db: Session, user_id: int) -> Optional[UserDB]:
        """Unban user"""
        user = self.get_by_id(db, user_id)
        if user:
            user.is_banned = False
            db.commit()
            db.refresh(user)
        return user
    
    def get_banned_users(self, db: Session) -> List[UserDB]:
        """Get all banned users"""
        return db.query(UserDB).filter(UserDB.is_banned == True).all()


# Singleton
user_repository = UserRepository()
