"""Admin panel business logic services"""

from sqlalchemy.orm import Session
from models import UserDB
from services.repository import user_repository
from typing import List, Optional


class AdminService:
    """Business logic for admin operations"""
    
    @staticmethod
    def get_all_admins(db: Session) -> List[UserDB]:
        """Get all admin users"""
        return user_repository.get_admins(db)
    
    @staticmethod
    def ban_user(db: Session, user_id: int, reason: Optional[str] = None) -> Optional[UserDB]:
        """Ban user with optional reason"""
        user = user_repository.ban_user(db, user_id)
        if user:
            print(f"User {user_id} ({user.email}) banned. Reason: {reason or 'No reason provided'}")
        return user
    
    @staticmethod
    def unban_user(db: Session, user_id: int) -> Optional[UserDB]:
        """Unban user"""
        user = user_repository.unban_user(db, user_id)
        if user:
            print(f"User {user_id} ({user.email}) unbanned")
        return user
    
    @staticmethod
    def get_user_ban_status(db: Session, user_id: int) -> Optional[dict]:
        """Get user ban status"""
        user = user_repository.get_by_id(db, user_id)
        if not user:
            return None
        
        return {
            "user_id": user.id,
            "email": user.email,
            "name": user.name,
            "is_banned": user.is_banned
        }
    
    @staticmethod
    def get_all_banned_users(db: Session) -> List[UserDB]:
        """Get all banned users"""
        return user_repository.get_banned_users(db)


# Singleton
admin_service = AdminService()
