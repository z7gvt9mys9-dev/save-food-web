"""Base repository for common CRUD operations"""

from sqlalchemy.orm import Session
from typing import TypeVar, Generic, List, Optional, Type

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """Base repository for common CRUD operations"""
    
    def __init__(self, model: Type[T]):
        self.model = model
    
    def create(self, db: Session, obj_in: dict) -> T:
        """Create new record"""
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_by_id(self, db: Session, id: int) -> Optional[T]:
        """Get record by ID"""
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all records with pagination"""
        return db.query(self.model).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_obj: T, obj_in: dict) -> T:
        """Update record"""
        for key, value in obj_in.items():
            setattr(db_obj, key, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Delete record"""
        db_obj = self.get_by_id(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False
