"""Donation repository for database operations"""

from sqlalchemy.orm import Session
from models import DonationDB
from .base_repository import BaseRepository
from typing import List


class DonationRepository(BaseRepository[DonationDB]):
    """Repository for Donation model"""
    
    def __init__(self):
        super().__init__(DonationDB)
    
    def get_by_user(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[DonationDB]:
        """Get donations by user"""
        return db.query(DonationDB).filter(DonationDB.user_id == user_id).offset(skip).limit(limit).all()
    
    def get_by_project(self, db: Session, project_id: int, skip: int = 0, limit: int = 100) -> List[DonationDB]:
        """Get donations for project"""
        return db.query(DonationDB).filter(DonationDB.project_id == project_id).offset(skip).limit(limit).all()
    
    def get_total_by_project(self, db: Session, project_id: int) -> float:
        """Get total donations for project"""
        result = db.query(DonationDB).filter(DonationDB.project_id == project_id).all()
        return sum(d.amount for d in result)


# Singleton
donation_repository = DonationRepository()
