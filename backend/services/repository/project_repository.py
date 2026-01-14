"""Project repository for database operations"""

from sqlalchemy.orm import Session
from models import ProjectDB
from .base_repository import BaseRepository
from typing import Optional, List


class ProjectRepository(BaseRepository[ProjectDB]):
    """Repository for Project model"""
    
    def __init__(self):
        super().__init__(ProjectDB)
    
    def get_by_owner(self, db: Session, owner_id: int, skip: int = 0, limit: int = 100) -> List[ProjectDB]:
        """Get projects by owner"""
        return db.query(ProjectDB).filter(ProjectDB.owner_id == owner_id).offset(skip).limit(limit).all()
    
    def get_verified(self, db: Session, skip: int = 0, limit: int = 100) -> List[ProjectDB]:
        """Get verified projects only"""
        return db.query(ProjectDB).filter(ProjectDB.is_verified == True).offset(skip).limit(limit).all()
    
    def get_by_status(self, db: Session, status: str, skip: int = 0, limit: int = 100) -> List[ProjectDB]:
        """Get projects by status"""
        return db.query(ProjectDB).filter(ProjectDB.status == status).offset(skip).limit(limit).all()


# Singleton
project_repository = ProjectRepository()
