"""Issue repository for database operations"""

from sqlalchemy.orm import Session
from models import IssueDB
from .base_repository import BaseRepository
from typing import Optional, List


class IssueRepository(BaseRepository[IssueDB]):
    """Repository for Issue model"""
    
    def __init__(self):
        super().__init__(IssueDB)
    
    def get_by_project(self, db: Session, project_id: int, skip: int = 0, limit: int = 100) -> List[IssueDB]:
        """Get issues by project"""
        return db.query(IssueDB).filter(IssueDB.project_id == project_id).offset(skip).limit(limit).all()
    
    def get_by_assignee(self, db: Session, assignee_id: int, skip: int = 0, limit: int = 100) -> List[IssueDB]:
        """Get issues assigned to user"""
        return db.query(IssueDB).filter(IssueDB.assignee_id == assignee_id).offset(skip).limit(limit).all()
    
    def get_by_status(self, db: Session, status: str, skip: int = 0, limit: int = 100) -> List[IssueDB]:
        """Get issues by status"""
        return db.query(IssueDB).filter(IssueDB.status == status).offset(skip).limit(limit).all()


# Singleton
issue_repository = IssueRepository()
