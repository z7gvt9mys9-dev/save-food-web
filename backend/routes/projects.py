"""Charity project management routes with transparent donation tracking"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import crud
from models import (
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectDetailResponse,
    DonationCreate, DonationResponse, DonationPublicResponse,
    CommentCreate, CommentResponse, CommentDetailResponse,
    SubscriptionCreate, SubscriptionResponse
)
from database import get_db
from routes.auth import get_current_user

router = APIRouter(prefix="/api/projects", tags=["projects"])


# ============ PROJECT ENDPOINTS ============

@router.get("", response_model=List[ProjectResponse])
async def get_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all projects (public listing)"""
    projects = crud.get_all_projects(db, skip=skip, limit=limit)
    return [ProjectResponse.from_orm(p) for p in projects]


@router.get("/verified", response_model=List[ProjectResponse])
async def get_verified_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get verified projects only"""
    projects = crud.get_verified_projects(db, skip=skip, limit=limit)
    return [ProjectResponse.from_orm(p) for p in projects]


@router.post("", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new charity project"""
    db_project = crud.create_project(
        db,
        owner_id=current_user.id,
        name=project_data.name,
        description=project_data.description or "",
        icon=project_data.icon or "📦",
        color=project_data.color or "#6b7280",
        goal_amount=project_data.goal_amount,
        latitude=project_data.latitude,
        longitude=project_data.longitude
    )
    return ProjectResponse.from_orm(db_project)


@router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project_detail(project_id: int, db: Session = Depends(get_db)):
    """Get project details with all information"""
    project = crud.get_project_by_id(db, project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    response = ProjectDetailResponse.from_orm(project)
    response.issues_count = len(project.issues)
    response.donations_count = len(project.donations)
    return response


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update project information"""
    project = crud.get_project_by_id(db, project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project owner can update"
        )
    
    updated_project = crud.update_project(
        db,
        project_id,
        name=project_update.name,
        description=project_update.description,
        icon=project_update.icon,
        color=project_update.color,
        goal_amount=project_update.goal_amount,
        report_url=project_update.report_url,
        latitude=project_update.latitude,
        longitude=project_update.longitude
    )
    
    return ProjectResponse.from_orm(updated_project)


@router.post("/{project_id}/verify")
async def verify_project(
    project_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify project as admin (only admins can verify)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can verify projects"
        )
    
    verified_project = crud.verify_project(db, project_id, current_user.id)
    
    if not verified_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return {
        "message": "Project verified",
        "project_id": project_id,
        "is_verified": True
    }


@router.post("/{project_id}/upload-report")
async def upload_report_url(
    project_id: int,
    report_url: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload PDF report URL for donation transparency"""
    project = crud.get_project_by_id(db, project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project owner or admin can upload reports"
        )
    
    updated_project = crud.update_project(db, project_id, report_url=report_url)
    
    return {
        "message": "Report URL uploaded",
        "project_id": project_id,
        "report_url": updated_project.report_url
    }


# ============ DONATION ENDPOINTS (TRANSPARENT CHARITY) ============

@router.post("/{project_id}/donations", response_model=DonationResponse)
async def donate_to_project(
    project_id: int,
    donation_data: DonationCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process donation in a transaction"""
    project = crud.get_project_by_id(db, project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    donation = crud.process_donation(
        db,
        user_id=current_user.id,
        project_id=project_id,
        amount=donation_data.amount,
        is_anonymous=donation_data.is_anonymous
    )
    
    if not donation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to process donation"
        )
    
    return DonationResponse.from_orm(donation)


@router.get("/{project_id}/donations", response_model=List[DonationPublicResponse])
async def get_public_donations(project_id: int, db: Session = Depends(get_db)):
    """Get public donation list (respects anonymity settings)"""
    project = crud.get_project_by_id(db, project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    public_donations = crud.get_public_donations(db, project_id)
    return public_donations


@router.get("/{project_id}/donation-summary")
async def get_donation_summary(project_id: int, db: Session = Depends(get_db)):
    """Get donation summary with progress"""
    project = crud.get_project_by_id(db, project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    progress_percent = 0
    if project.goal_amount > 0:
        progress_percent = min(100, (project.current_amount / project.goal_amount) * 100)
    
    return {
        "project_id": project_id,
        "goal_amount": project.goal_amount,
        "current_amount": project.current_amount,
        "progress_percent": round(progress_percent, 2),
        "is_completed": project.current_amount >= project.goal_amount,
        "total_donors": len(project.donations)
    }


# ============ COMMENT ENDPOINTS ============

@router.post("/{project_id}/comments", response_model=CommentResponse)
async def create_comment(
    project_id: int,
    comment_data: CommentCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a comment on a project"""
    project = crud.get_project_by_id(db, project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    comment = crud.create_comment(
        db,
        user_id=current_user.id,
        project_id=project_id,
        content=comment_data.content
    )
    
    return CommentResponse.from_orm(comment)


@router.get("/{project_id}/comments", response_model=List[CommentDetailResponse])
async def get_project_comments(project_id: int, skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """Get all comments for a project"""
    project = crud.get_project_by_id(db, project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    comments = crud.get_comments_by_project(db, project_id, skip=skip, limit=limit)
    return [CommentDetailResponse.from_orm(c) for c in comments]


@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a comment (only author or admin can delete)"""
    from models import CommentDB
    comment = db.query(CommentDB).filter(CommentDB.id == comment_id).first()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    if comment.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only comment author or admin can delete"
        )
    
    crud.delete_comment(db, comment_id)
    
    return {"message": "Comment deleted"}


# ============ SUBSCRIPTION ENDPOINTS ============

@router.post("/{project_id}/subscribe", response_model=SubscriptionResponse)
async def subscribe_to_project(
    project_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Subscribe to project notifications"""
    project = crud.get_project_by_id(db, project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    subscription = crud.subscribe_to_project(db, current_user.id, project_id)
    
    return SubscriptionResponse.from_orm(subscription)


@router.delete("/{project_id}/unsubscribe")
async def unsubscribe_from_project(
    project_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Unsubscribe from project notifications"""
    success = crud.unsubscribe_from_project(db, current_user.id, project_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    return {"message": "Unsubscribed from project"}

