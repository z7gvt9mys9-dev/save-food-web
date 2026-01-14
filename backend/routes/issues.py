"""Volunteer task and issue management routes"""

from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from typing import List, Optional
import crud
from models import (
    IssueCreate, IssueUpdate, IssueResponse, IssueDetailResponse,
    IssueCategory, IssueStatusUpdate
)
from database import get_db
from routes.auth import get_current_user

router = APIRouter(prefix="/api/issues", tags=["issues"])


# ============ ISSUE ENDPOINTS ============

@router.get("", response_model=List[IssueResponse])
async def get_issues(
    project_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get issues, optionally filtered by project"""
    if project_id:
        issues = crud.get_issues_by_project(db, project_id, skip=skip, limit=limit)
    else:
        from models import IssueDB
        issues = db.query(IssueDB).offset(skip).limit(limit).all()
    
    return [IssueResponse.from_orm(issue) for issue in issues]


@router.post("", response_model=IssueResponse)
async def create_issue(
    issue_data: IssueCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new volunteer task/issue"""
    # Check if project exists
    project = crud.get_project_by_id(db, issue_data.project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    db_issue = crud.create_issue(
        db,
        project_id=issue_data.project_id,
        reporter_id=current_user.id,
        title=issue_data.title,
        description=issue_data.description or "",
        category=issue_data.category,
        priority=issue_data.priority,
        due_date=issue_data.due_date
    )
    
    return IssueResponse.from_orm(db_issue)


@router.get("/{issue_id}", response_model=IssueDetailResponse)
async def get_issue_detail(issue_id: int, db: Session = Depends(get_db)):
    """Get issue details with all relationships"""
    issue = crud.get_issue_by_id(db, issue_id)
    
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    
    return IssueDetailResponse.from_orm(issue)


@router.put("/{issue_id}", response_model=IssueResponse)
async def update_issue(
    issue_id: int,
    issue_update: IssueUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update issue information"""
    issue = crud.get_issue_by_id(db, issue_id)
    
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    
    # Only reporter or project owner can update
    if issue.reporter_id != current_user.id and issue.project.owner_id != current_user.id:
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only issue reporter or project owner can update"
            )
    
    updated_issue = crud.update_issue(
        db,
        issue_id,
        title=issue_update.title,
        description=issue_update.description,
        status=issue_update.status,
        category=issue_update.category,
        priority=issue_update.priority
    )
    
    return IssueResponse.from_orm(updated_issue)


# ============ VOLUNTEER ASSIGNMENT (GAMIFICATION) ============

@router.post("/{issue_id}/assign", response_model=IssueResponse)
async def assign_volunteer(
    issue_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Assign current user as volunteer to the issue"""
    issue = crud.get_issue_by_id(db, issue_id)
    
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    
    if issue.status == "closed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot assign to closed issue"
        )
    
    assigned_issue = crud.assign_volunteer(db, issue_id, current_user.id)
    
    return IssueResponse.from_orm(assigned_issue)


@router.post("/{issue_id}/close", response_model=IssueResponse)
async def close_issue(
    issue_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Close an issue and award XP to assignee"""
    issue = crud.get_issue_by_id(db, issue_id)
    
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    
    # Only reporter or project owner can close
    if issue.reporter_id != current_user.id and issue.project.owner_id != current_user.id:
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only issue reporter or project owner can close"
            )
    
    closed_issue = crud.close_issue(db, issue_id)
    
    if not closed_issue or not closed_issue.assignee_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Issue must be assigned to a volunteer before closing"
        )
    
    return IssueResponse.from_orm(closed_issue)


@router.get("/{issue_id}/assignee-stats")
async def get_assignee_stats(issue_id: int, db: Session = Depends(get_db)):
    """Get stats about the volunteer assigned to this issue"""
    issue = crud.get_issue_by_id(db, issue_id)
    
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    
    if not issue.assignee:
        return {"message": "No volunteer assigned to this issue"}
    
    return {
        "assignee_id": issue.assignee.id,
        "assignee_name": issue.assignee.name,
        "xp": issue.assignee.xp,
        "rating_level": issue.assignee.rating_level,
        "issues_completed": len([i for i in issue.assignee.issues_assigned if i.status == "closed"])
    }


@router.delete("/{issue_id}")
async def delete_issue(
    issue_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an issue (only reporter or admin can delete)"""
    issue = crud.get_issue_by_id(db, issue_id)
    
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    
    if issue.reporter_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only issue reporter or admin can delete"
        )
    
    from models import IssueDB
    db.delete(issue)
    db.commit()
    
    return {"message": "Issue deleted"}

    return new_issue


@router.get("/{issue_id}", response_model=dict)
async def get_issue(issue_id: str, authorization: Optional[str] = Header(None)):
    """Get issue details"""
    user_id = get_user_from_token(authorization)
    
    issue = issues_db.get(issue_id)
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    
    # Check if user has access to project
    project = projects_db.get(issue["projectId"])
    if project and user_id not in project["members"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this issue"
        )
    
    return issue


@router.put("/{issue_id}", response_model=dict)
async def update_issue(issue_id: str, updates: IssueUpdate, authorization: Optional[str] = Header(None)):
    """Update issue"""
    user_id = get_user_from_token(authorization)
    
    issue = issues_db.get(issue_id)
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    
    # Check if user is issue creator
    if issue["createdBy"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only issue creator can update"
        )
    
    if updates.title:
        issue["title"] = updates.title
    if updates.description is not None:
        issue["description"] = updates.description
    if updates.priority:
        issue["priority"] = updates.priority
    if updates.assignedTo is not None:
        issue["assignedTo"] = updates.assignedTo
    
    return issue


@router.patch("/{issue_id}/status", response_model=dict)
async def update_issue_status(issue_id: str, update: IssueStatusUpdate, authorization: Optional[str] = Header(None)):
    """Update issue status"""
    user_id = get_user_from_token(authorization)
    
    issue = issues_db.get(issue_id)
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    
    # Check if user is in project
    project = projects_db.get(issue["projectId"])
    if project and user_id not in project["members"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this issue"
        )
    
    issue["status"] = update.status
    
    return issue


@router.delete("/{issue_id}", response_model=dict)
async def delete_issue(issue_id: str, authorization: Optional[str] = Header(None)):
    """Delete issue"""
    user_id = get_user_from_token(authorization)
    
    issue = issues_db.get(issue_id)
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    
    # Only creator can delete
    if issue["createdBy"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only issue creator can delete"
        )
    
    del issues_db[issue_id]
    
    return {"message": f"Issue {issue_id} deleted"}


@router.get("/project/{project_id}/stats", response_model=dict)
async def get_project_stats(project_id: str, authorization: Optional[str] = Header(None)):
    """Get issue statistics for a project"""
    user_id = get_user_from_token(authorization)
    
    project = projects_db.get(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if user_id not in project["members"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    open_count = 0
    closed_count = 0
    in_progress_count = 0
    
    for issue in issues_db.values():
        if issue["projectId"] == project_id:
            if issue["status"] == "open":
                open_count += 1
            elif issue["status"] == "closed":
                closed_count += 1
            elif issue["status"] == "in-progress":
                in_progress_count += 1
    
    return {
        "projectId": project_id,
        "open": open_count,
        "closed": closed_count,
        "inProgress": in_progress_count,
        "total": open_count + closed_count + in_progress_count
    }
