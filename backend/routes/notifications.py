"""Notification management routes"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import crud
from models import SubscriptionResponse
from database import get_db
from routes.auth import get_current_user

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.post("/")
async def create_notification(
    data: dict,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new notification for current user"""
    # This endpoint creates a simple notification response
    return {
        "id": 1,
        "title": data.get("title", "Notification"),
        "message": data.get("message", ""),
        "type": data.get("type", "info"),
        "order": data.get("order", ""),
        "street": data.get("street", ""),
        "read": False,
        "created_at": "2024-01-08T00:00:00"
    }


@router.get("/subscriptions", response_model=List[SubscriptionResponse])
async def get_my_subscriptions(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all project subscriptions for current user"""
    from models import SubscriptionDB
    subscriptions = db.query(SubscriptionDB).filter(
        SubscriptionDB.user_id == current_user.id
    ).all()
    
    return [SubscriptionResponse.from_orm(s) for s in subscriptions]


@router.get("/subscriptions/{project_id}")
async def get_project_subscribers(
    project_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all subscribers to a project (admin only)"""
    project = crud.get_project_by_id(db, project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project owner or admin can view subscribers"
        )
    
    subscribers = crud.get_project_subscribers(db, project_id)
    
    return {
        "project_id": project_id,
        "subscriber_count": len(subscribers),
        "subscribers": [
            {
                "user_id": s.id,
                "name": s.name,
                "email": s.email
            } for s in subscribers
        ]
    }


@router.get("/donations/new")
async def get_donation_notifications(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get recent donations for notification display"""
    from models import DonationDB
    donations = db.query(DonationDB).order_by(
        DonationDB.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    result = []
    for donation in donations:
        donor_name = None if donation.is_anonymous else donation.user.name
        result.append({
            "id": donation.id,
            "donor_name": donor_name,
            "amount": donation.amount,
            "order": donation.project.name,
            "street": donation.project.description or "Местоположение не указано",
            "project_name": donation.project.name,
            "created_at": donation.created_at
        })
    
    return result


@router.get("/volunteers/completed")
async def get_volunteer_completions(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get recently completed volunteer tasks for notifications"""
    from models import IssueDB
    completed_issues = db.query(IssueDB).filter(
        IssueDB.status == "closed"
    ).order_by(
        IssueDB.updated_at.desc()
    ).offset(skip).limit(limit).all()
    
    result = []
    for issue in completed_issues:
        if issue.assignee:
            result.append({
                "issue_id": issue.id,
                "issue_title": issue.title,
                "volunteer_name": issue.assignee.name,
                "volunteer_xp_gained": {
                    "low": 10,
                    "medium": 25,
                    "high": 50
                }.get(issue.priority, 25),
                "project_name": issue.project.name,
                "completed_at": issue.updated_at
            })
    
    return result


@router.get("/projects/new")
async def get_new_projects(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get recently created projects for notifications"""
    from models import ProjectDB
    projects = db.query(ProjectDB).order_by(
        ProjectDB.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    result = []
    for project in projects:
        result.append({
            "project_id": project.id,
            "project_name": project.name,
            "order": project.name,
            "street": project.description or "Местоположение не указано",
            "owner_name": project.owner.name,
            "goal_amount": project.goal_amount,
            "is_verified": project.is_verified,
            "created_at": project.created_at
        })
    
    return result

