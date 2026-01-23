from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum as PyEnum
from database import Base


class UserRole(str, PyEnum):
    DONOR = "Donor"
    RECIPIENT = "Recipient"
    COURIER = "Courier"
    ADMINISTRATOR = "Administrator"


class ProjectStatus(str, PyEnum):
    ACTIVE = "Active"
    IN_PROGRESS = "In_Progress"
    COMPLETED = "Completed"
    ARCHIVED = "Archived"


class IssueCategory(str, PyEnum):
    """Issue/Task category enum"""
    HANDS = "Hands"
    TRANSPORT = "Transport"
    ITEMS = "Items"


class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    avatar = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.DONOR)
    
    # Gamification & Admin
    xp = Column(Integer, default=0)
    rating_level = Column(String, default="Bronze")
    is_admin = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)
    
    # Courier stats
    courier_deliveries = Column(Integer, default=0)
    courier_rating = Column(Float, default=5.0)
    courier_avg_delivery_time = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    projects = relationship("ProjectDB", back_populates="owner", foreign_keys="ProjectDB.owner_id")
    issues_created = relationship("IssueDB", back_populates="reporter", foreign_keys="IssueDB.reporter_id")
    issues_assigned = relationship("IssueDB", back_populates="assignee", foreign_keys="IssueDB.assignee_id")
    donations = relationship("DonationDB", back_populates="user")
    comments = relationship("CommentDB", back_populates="user")
    subscriptions = relationship("SubscriptionDB", back_populates="user")
    deliveries = relationship("DeliveryDB", back_populates="courier", foreign_keys="DeliveryDB.courier_id")


class ProjectDB(Base):
    """Charity project database model"""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String, default="box")
    color = Column(String, default="#6b7280")
    
    # Finance tracking
    goal_amount = Column(Float, nullable=False, default=0.0)
    current_amount = Column(Float, nullable=False, default=0.0)
    report_url = Column(String, nullable=True)
    
    # Status & Verification
    status = Column(Enum(ProjectStatus), default=ProjectStatus.ACTIVE)
    is_verified = Column(Boolean, default=False)
    
    # Geolocation
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Foreign key
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    owner = relationship("UserDB", back_populates="projects", foreign_keys=[owner_id])
    issues = relationship("IssueDB", back_populates="project", cascade="all, delete-orphan")
    donations = relationship("DonationDB", back_populates="project", cascade="all, delete-orphan")
    comments = relationship("CommentDB", back_populates="project", cascade="all, delete-orphan")
    subscriptions = relationship("SubscriptionDB", back_populates="project", cascade="all, delete-orphan")


class IssueDB(Base):
    """Volunteer task database model"""
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Category for volunteer type
    category = Column(Enum(IssueCategory), default=IssueCategory.HANDS)
    
    # Status
    status = Column(String, default="open")
    priority = Column(String, default="medium")
    
    # Foreign keys
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    due_date = Column(DateTime, nullable=True)

    # Relationships
    project = relationship("ProjectDB", back_populates="issues", foreign_keys=[project_id])
    reporter = relationship("UserDB", back_populates="issues_created", foreign_keys=[reporter_id])
    assignee = relationship("UserDB", back_populates="issues_assigned", foreign_keys=[assignee_id])


class DonationDB(Base):
    """Donation transaction history for transparency"""
    __tablename__ = "donations"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    is_anonymous = Column(Boolean, default=False)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    user = relationship("UserDB", back_populates="donations")
    project = relationship("ProjectDB", back_populates="donations")


class CommentDB(Base):
    """Project discussion comments"""
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("UserDB", back_populates="comments")
    project = relationship("ProjectDB", back_populates="comments")


class SubscriptionDB(Base):
    """User subscriptions to project notifications"""
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    user = relationship("UserDB", back_populates="subscriptions")
    project = relationship("ProjectDB", back_populates="subscriptions")


class DeliveryDB(Base):
    """Courier delivery orders"""
    __tablename__ = "deliveries"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    courier_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    status = Column(String, default="pending")
    rating = Column(Float, nullable=True)
    delivery_time_minutes = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    accepted_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    project = relationship("ProjectDB")
    courier = relationship("UserDB", back_populates="deliveries", foreign_keys=[courier_id])


class ParcelLockerDB(Base):
    """Parcel locker storage locations"""
    __tablename__ = "parcel_lockers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Capacity
    total_capacity = Column(Integer, default=50)
    current_occupancy = Column(Integer, default=0)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())



class UserBase(BaseModel):
    name: str
    email: str


class UserCreate(UserBase):
    password: str
    role: Optional[str] = UserRole.DONOR


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    avatar: Optional[str] = None
    role: str = UserRole.DONOR
    xp: int = 0
    rating_level: str = "Bronze"
    is_admin: bool = False
    is_banned: bool = False
    courier_deliveries: int = 0
    courier_rating: float = 5.0
    courier_avg_delivery_time: float = 0.0
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    name: Optional[str] = None
    avatar: Optional[str] = None
    password: Optional[str] = None
    old_password: Optional[str] = None  # Required if changing password

class AuthResponse(BaseModel):
    token: str
    user: UserResponse

class LoginRequest(BaseModel):
    email: str
    password: str



class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = ""
    icon: Optional[str] = ""
    color: Optional[str] = "#6b7280"
    goal_amount: float = 0.0
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    goal_amount: Optional[float] = None
    report_url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    icon: str | None = None
    color: str | None = "#4CAF50"
    goal_amount: float
    current_amount: float
    report_url: Optional[str] = None
    status: str = "Active"
    is_verified: bool = False
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectDetailResponse(ProjectResponse):
    owner: UserResponse
    issues_count: Optional[int] = 0
    donations_count: Optional[int] = 0



class IssueBase(BaseModel):
    title: str
    description: Optional[str] = ""
    project_id: int
    category: IssueCategory = IssueCategory.HANDS
    priority: Optional[str] = "medium"
    due_date: Optional[datetime] = None


class IssueCreate(IssueBase):
    pass


class IssueUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    category: Optional[IssueCategory] = None
    priority: Optional[str] = None
    assignee_id: Optional[int] = None
    due_date: Optional[datetime] = None


class IssueStatusUpdate(BaseModel):
    status: str
    assignee_id: Optional[int] = None


class IssueResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    project_id: int
    category: str
    status: str
    priority: str
    reporter_id: int
    assignee_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    due_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class IssueDetailResponse(IssueResponse):
    reporter: UserResponse
    assignee: Optional[UserResponse] = None
    project: ProjectResponse



class DonationCreate(BaseModel):
    amount: float
    project_id: int
    is_anonymous: bool = False


class DonationResponse(BaseModel):
    id: int
    amount: float
    is_anonymous: bool
    user_id: int
    project_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class DonationPublicResponse(BaseModel):
    """Public donation view - hides donor name if anonymous"""
    id: int
    amount: float
    donor_name: Optional[str] = None
    project_id: int
    created_at: datetime



class CommentCreate(BaseModel):
    content: str
    project_id: int


class CommentResponse(BaseModel):
    id: int
    content: str
    user_id: int
    project_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CommentDetailResponse(CommentResponse):
    user: UserResponse



class SubscriptionCreate(BaseModel):
    project_id: int


class SubscriptionResponse(BaseModel):
    id: int
    user_id: int
    project_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class DeliveryCreate(BaseModel):
    project_id: int


class DeliveryResponse(BaseModel):
    id: int
    project_id: int
    courier_id: Optional[int] = None
    status: str
    rating: Optional[float] = None
    delivery_time_minutes: Optional[int] = None
    created_at: datetime
    accepted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DeliveryDetailResponse(DeliveryResponse):
    project: ProjectResponse
    courier: Optional[UserResponse] = None


class ParcelLockerResponse(BaseModel):
    id: int
    name: str
    address: str
    latitude: float
    longitude: float
    total_capacity: int
    current_occupancy: int
    is_active: bool
    available_slots: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
    
    @property
    def available_slots(self) -> int:
        return self.total_capacity - self.current_occupancy


class ErrorResponse(BaseModel):
    error: str


class MessageResponse(BaseModel):
    message: str

