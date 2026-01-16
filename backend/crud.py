"""CRUD operations for database models"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from models import (
    UserDB, ProjectDB, IssueDB, DonationDB, CommentDB, SubscriptionDB, DeliveryDB,
    ProjectStatus, IssueCategory, UserRole
)
from auth import hash_password, verify_password
from typing import Optional, List


# ============ USER CRUD ============

def create_user(db: Session, email: str, name: str, password: str, role: Optional[str] = None) -> UserDB:
    """Create a new user"""
    db_user = UserDB(
        email=email,
        name=name,
        password_hash=hash_password(password),
        role=role or UserRole.DONOR,
        xp=0,
        rating_level="Bronze",
        is_admin=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_id(db: Session, user_id: int) -> Optional[UserDB]:
    """Get user by ID"""
    return db.query(UserDB).filter(UserDB.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[UserDB]:
    """Get user by email"""
    return db.query(UserDB).filter(UserDB.email == email).first()


def update_user(db: Session, user_id: int, name: Optional[str] = None,
                avatar: Optional[str] = None, password: Optional[str] = None) -> UserDB:
    """Update user information"""
    db_user = get_user_by_id(db, user_id)
    if db_user:
        if name:
            db_user.name = name
        if avatar:
            db_user.avatar = avatar
        if password:
            db_user.password_hash = hash_password(password)
        db.commit()
        db.refresh(db_user)
    return db_user


def add_xp_to_user(db: Session, user_id: int, xp_amount: int) -> UserDB:
    """Add XP to user for gamification"""
    db_user = get_user_by_id(db, user_id)
    if db_user:
        db_user.xp += xp_amount
        # Update rating level based on XP
        if db_user.xp >= 1000:
            db_user.rating_level = "Gold"
        elif db_user.xp >= 500:
            db_user.rating_level = "Silver"
        else:
            db_user.rating_level = "Bronze"
        db.commit()
        db.refresh(db_user)
    return db_user


# ============ PROJECT CRUD ============

def create_project(db: Session, owner_id: int, name: str, description: str,
                   icon: str, color: str, goal_amount: float,
                   latitude: Optional[float] = None,
                   longitude: Optional[float] = None) -> ProjectDB:
    """Create a new charity project"""
    db_project = ProjectDB(
        owner_id=owner_id,
        name=name,
        description=description,
        icon=icon,
        color=color,
        goal_amount=goal_amount,
        current_amount=0.0,
        status=ProjectStatus.ACTIVE,
        is_verified=False,
        latitude=latitude,
        longitude=longitude
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def get_project_by_id(db: Session, project_id: int) -> Optional[ProjectDB]:
    """Get project by ID"""
    return db.query(ProjectDB).filter(ProjectDB.id == project_id).first()


def get_all_projects(db: Session, skip: int = 0, limit: int = 100) -> List[ProjectDB]:
    """Get all projects with pagination"""
    return db.query(ProjectDB).offset(skip).limit(limit).all()


def get_verified_projects(db: Session, skip: int = 0, limit: int = 100) -> List[ProjectDB]:
    """Get verified projects only"""
    return db.query(ProjectDB).filter(ProjectDB.is_verified == True).offset(skip).limit(limit).all()


def update_project(db: Session, project_id: int, name: Optional[str] = None,
                   description: Optional[str] = None, icon: Optional[str] = None,
                   color: Optional[str] = None, goal_amount: Optional[float] = None,
                   report_url: Optional[str] = None, latitude: Optional[float] = None,
                   longitude: Optional[float] = None) -> Optional[ProjectDB]:
    """Update project information"""
    db_project = get_project_by_id(db, project_id)
    if db_project:
        if name:
            db_project.name = name
        if description:
            db_project.description = description
        if icon:
            db_project.icon = icon
        if color:
            db_project.color = color
        if goal_amount is not None:
            db_project.goal_amount = goal_amount
        if report_url:
            db_project.report_url = report_url
        if latitude is not None:
            db_project.latitude = latitude
        if longitude is not None:
            db_project.longitude = longitude
        db.commit()
        db.refresh(db_project)
    return db_project


def verify_project(db: Session, project_id: int, admin_id: int) -> Optional[ProjectDB]:
    """Verify project (admin only)"""
    admin = get_user_by_id(db, admin_id)
    if not admin or not admin.is_admin:
        return None
    
    db_project = get_project_by_id(db, project_id)
    if db_project:
        db_project.is_verified = True
        db.commit()
        db.refresh(db_project)
    return db_project


def unverify_project(db: Session, project_id: int, admin_id: int) -> Optional[ProjectDB]:
    """Unverify project (admin only)"""
    admin = get_user_by_id(db, admin_id)
    if not admin or not admin.is_admin:
        return None
    
    db_project = get_project_by_id(db, project_id)
    if db_project:
        db_project.is_verified = False
        db.commit()
        db.refresh(db_project)
    return db_project


def update_project_status(db: Session, project_id: int, status: ProjectStatus) -> Optional[ProjectDB]:
    """Update project status"""
    db_project = get_project_by_id(db, project_id)
    if db_project:
        db_project.status = status
        db.commit()
        db.refresh(db_project)
    return db_project


# ============ DONATION CRUD & TRANSACTIONS ============

def process_donation(db: Session, user_id: int, project_id: int,
                     amount: float, is_anonymous: bool = False) -> Optional[DonationDB]:
    """
    Process donation in a single transaction:
    1. Create donation record
    2. Update project current_amount
    """
    try:
        # Create donation record
        db_donation = DonationDB(
            user_id=user_id,
            project_id=project_id,
            amount=amount,
            is_anonymous=is_anonymous
        )
        db.add(db_donation)
        
        # Update project current amount
        db_project = get_project_by_id(db, project_id)
        if db_project:
            db_project.current_amount += amount
        
        db.commit()
        db.refresh(db_donation)
        return db_donation
    except Exception as e:
        db.rollback()
        print(f"Error processing donation: {e}")
        return None


def get_donations_by_project(db: Session, project_id: int, skip: int = 0,
                             limit: int = 100) -> List[DonationDB]:
    """Get all donations for a project"""
    return db.query(DonationDB).filter(
        DonationDB.project_id == project_id
    ).offset(skip).limit(limit).all()


def get_public_donations(db: Session, project_id: int) -> List[dict]:
    """Get public donation list (hides anonymous donor names)"""
    donations = get_donations_by_project(db, project_id)
    result = []
    for donation in donations:
        donor_name = None if donation.is_anonymous else donation.user.name
        result.append({
            "id": donation.id,
            "amount": donation.amount,
            "donor_name": donor_name,
            "project_id": donation.project_id,
            "created_at": donation.created_at
        })
    return result


# ============ ISSUE CRUD ============

def create_issue(db: Session, project_id: int, reporter_id: int, title: str,
                description: str, category: IssueCategory = IssueCategory.HANDS,
                priority: str = "medium", due_date: Optional[str] = None) -> IssueDB:
    """Create a new volunteer task/issue"""
    db_issue = IssueDB(
        project_id=project_id,
        reporter_id=reporter_id,
        title=title,
        description=description,
        category=category,
        priority=priority,
        due_date=due_date,
        status="open",
        assignee_id=None
    )
    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)
    return db_issue


def get_issue_by_id(db: Session, issue_id: int) -> Optional[IssueDB]:
    """Get issue by ID"""
    return db.query(IssueDB).filter(IssueDB.id == issue_id).first()


def get_issues_by_project(db: Session, project_id: int, skip: int = 0,
                          limit: int = 100) -> List[IssueDB]:
    """Get all issues for a project"""
    return db.query(IssueDB).filter(
        IssueDB.project_id == project_id
    ).offset(skip).limit(limit).all()


def assign_volunteer(db: Session, issue_id: int, volunteer_id: int) -> Optional[IssueDB]:
    """Assign a volunteer to an issue"""
    db_issue = get_issue_by_id(db, issue_id)
    if db_issue:
        db_issue.assignee_id = volunteer_id
        db_issue.status = "in-progress"
        db.commit()
        db.refresh(db_issue)
    return db_issue


def close_issue(db: Session, issue_id: int) -> Optional[IssueDB]:
    """
    Close an issue and award XP to assignee:
    1. Update issue status
    2. Award XP to volunteer
    """
    db_issue = get_issue_by_id(db, issue_id)
    if db_issue and db_issue.assignee_id:
        db_issue.status = "closed"
        
        # Award XP based on priority
        xp_reward = {
            "low": 10,
            "medium": 25,
            "high": 50
        }.get(db_issue.priority, 25)
        
        add_xp_to_user(db, db_issue.assignee_id, xp_reward)
        db.commit()
        db.refresh(db_issue)
    return db_issue


def update_issue(db: Session, issue_id: int, title: Optional[str] = None,
                 description: Optional[str] = None, status: Optional[str] = None,
                 category: Optional[IssueCategory] = None,
                 priority: Optional[str] = None) -> Optional[IssueDB]:
    """Update issue information"""
    db_issue = get_issue_by_id(db, issue_id)
    if db_issue:
        if title:
            db_issue.title = title
        if description:
            db_issue.description = description
        if status:
            db_issue.status = status
        if category:
            db_issue.category = category
        if priority:
            db_issue.priority = priority
        db.commit()
        db.refresh(db_issue)
    return db_issue


# ============ COMMENT CRUD ============

def create_comment(db: Session, user_id: int, project_id: int, content: str) -> CommentDB:
    """Create a project comment"""
    db_comment = CommentDB(
        user_id=user_id,
        project_id=project_id,
        content=content
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def get_comments_by_project(db: Session, project_id: int, skip: int = 0,
                            limit: int = 100) -> List[CommentDB]:
    """Get all comments for a project"""
    return db.query(CommentDB).filter(
        CommentDB.project_id == project_id
    ).offset(skip).limit(limit).all()


def delete_comment(db: Session, comment_id: int) -> bool:
    """Delete a comment"""
    db_comment = db.query(CommentDB).filter(CommentDB.id == comment_id).first()
    if db_comment:
        db.delete(db_comment)
        db.commit()
        return True
    return False


# ============ SUBSCRIPTION CRUD ============

def subscribe_to_project(db: Session, user_id: int, project_id: int) -> Optional[SubscriptionDB]:
    """Subscribe user to project notifications"""
    # Check if already subscribed
    existing = db.query(SubscriptionDB).filter(
        and_(
            SubscriptionDB.user_id == user_id,
            SubscriptionDB.project_id == project_id
        )
    ).first()
    
    if existing:
        return existing
    
    db_subscription = SubscriptionDB(
        user_id=user_id,
        project_id=project_id
    )
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    return db_subscription


def unsubscribe_from_project(db: Session, user_id: int, project_id: int) -> bool:
    """Unsubscribe user from project notifications"""
    db_subscription = db.query(SubscriptionDB).filter(
        and_(
            SubscriptionDB.user_id == user_id,
            SubscriptionDB.project_id == project_id
        )
    ).first()
    
    if db_subscription:
        db.delete(db_subscription)
        db.commit()
        return True
    return False


def get_project_subscribers(db: Session, project_id: int) -> List[UserDB]:
    """Get all users subscribed to a project"""
    subscriptions = db.query(SubscriptionDB).filter(
        SubscriptionDB.project_id == project_id
    ).all()
    return [sub.user for sub in subscriptions]


def create_delivery(db: Session, project_id: int) -> DeliveryDB:
    """Create a new delivery order"""
    db_delivery = DeliveryDB(
        project_id=project_id,
        status="pending"
    )
    db.add(db_delivery)
    db.commit()
    db.refresh(db_delivery)
    return db_delivery


def accept_delivery(db: Session, delivery_id: int, courier_id: int) -> Optional[DeliveryDB]:
    """Accept delivery order"""
    from datetime import datetime
    db_delivery = db.query(DeliveryDB).filter(DeliveryDB.id == delivery_id).first()
    
    if db_delivery:
        db_delivery.courier_id = courier_id
        db_delivery.status = "accepted"
        db_delivery.accepted_at = datetime.utcnow()
        db.commit()
        db.refresh(db_delivery)
    
    return db_delivery


def complete_delivery(db: Session, delivery_id: int, delivery_time_minutes: int, rating: float) -> Optional[DeliveryDB]:
    """Complete delivery and update courier stats"""
    from datetime import datetime
    db_delivery = db.query(DeliveryDB).filter(DeliveryDB.id == delivery_id).first()
    
    if db_delivery and db_delivery.courier_id:
        db_delivery.status = "completed"
        db_delivery.delivery_time_minutes = delivery_time_minutes
        db_delivery.rating = rating
        db_delivery.completed_at = datetime.utcnow()
        
        courier = get_user_by_id(db, db_delivery.courier_id)
        if courier:
            old_deliveries = courier.courier_deliveries
            old_rating = courier.courier_rating
            old_time = courier.courier_avg_delivery_time
            
            courier.courier_deliveries += 1
            courier.courier_rating = (old_rating * old_deliveries + rating) / courier.courier_deliveries
            courier.courier_avg_delivery_time = (old_time * old_deliveries + delivery_time_minutes) / courier.courier_deliveries
        
        db.commit()
        db.refresh(db_delivery)
    
    return db_delivery


def get_all_pending_deliveries(db: Session) -> List[DeliveryDB]:
    """Get all pending delivery orders"""
    return db.query(DeliveryDB).filter(DeliveryDB.status == "pending").all()


def get_delivery_by_id(db: Session, delivery_id: int) -> Optional[DeliveryDB]:
    """Get delivery by ID"""
    return db.query(DeliveryDB).filter(DeliveryDB.id == delivery_id).first()
