from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from math import radians, sin, cos, sqrt, atan2
import logging

from models import (
    ProjectDB, ProjectCreate, ProjectUpdate, ProjectResponse, ProjectDetailResponse,
)
from database import get_db
from routes.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/projects", tags=["projects"])

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371
    
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    return R * c

@router.get("", response_model=List[ProjectResponse])
async def get_all_projects(
    skip: int = 0,
    limit: int = 100,
    userId: Optional[int] = None,
    db: Session = Depends(get_db)
) -> List[ProjectResponse]:
    try:
        limit = min(limit, 1000)
        
        query = db.query(ProjectDB)
        
        if userId is not None:
            query = query.filter(ProjectDB.owner_id == userId)
        
        projects = query.offset(skip).limit(limit).all()
        logger.info(f"GET /projects - Fetched {len(projects)} projects")
        
        return [ProjectResponse.from_orm(p) for p in projects]
    
    except Exception as e:
        logger.error(f"GET /projects - Error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch projects: {str(e)}"
        )


@router.get("/verified", response_model=List[ProjectResponse])
async def get_verified_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> List[ProjectResponse]:
    try:
        limit = min(limit, 1000)
        
        projects = db.query(ProjectDB).filter(
            ProjectDB.is_verified == True
        ).offset(skip).limit(limit).all()
        
        logger.info(f"GET /projects/verified - Fetched {len(projects)} projects")
        
        return [ProjectResponse.from_orm(p) for p in projects]
    
    except Exception as e:
        logger.error(f"GET /projects/verified - Error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch verified projects: {str(e)}"
        )


@router.get("/nearby/all", response_model=List[ProjectResponse])
async def get_nearby_projects(
    latitude: float = 55.7536,
    longitude: float = 37.6201,
    radius_km: float = 50,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> List[ProjectResponse]:
    try:
        limit = min(limit, 1000)
        
        projects = db.query(ProjectDB).filter(
            ProjectDB.latitude.isnot(None),
            ProjectDB.longitude.isnot(None)
        ).offset(skip).limit(limit).all()
        
        nearby = [
            p for p in projects
            if haversine_distance(latitude, longitude, p.latitude, p.longitude) <= radius_km
        ]
        
        logger.info(f"GET /projects/nearby/all - Found {len(nearby)} projects")
        
        return [ProjectResponse.from_orm(p) for p in nearby]
    
    except Exception as e:
        logger.error(f"GET /projects/nearby/all - Error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch nearby projects: {str(e)}"
        )


@router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project_by_id(
    project_id: int,
    db: Session = Depends(get_db)
) -> ProjectDetailResponse:
    try:
        project = db.query(ProjectDB).filter(ProjectDB.id == project_id).first()
        
        if not project:
            logger.warning(f"GET /projects/{project_id} - Not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found"
            )
        
        response = ProjectDetailResponse.from_orm(project)
        response.issues_count = len(project.issues) if project.issues else 0
        response.donations_count = len(project.donations) if project.donations else 0
        
        logger.info(f"GET /projects/{project_id} - Retrieved")
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"GET /projects/{project_id} - Error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch project details: {str(e)}"
        )


@router.post("", response_model=ProjectResponse)
async def create_new_project(
    project_data: ProjectCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ProjectResponse:
    try:
        db_project = ProjectDB(
            owner_id=current_user.id,
            name=project_data.name,
            description=project_data.description or "",
            icon=project_data.icon or "box",
            color=project_data.color or "#6b7280",
            goal_amount=project_data.goal_amount,
            current_amount=0.0,
            latitude=project_data.latitude,
            longitude=project_data.longitude,
            is_verified=False,
            status="Active"
        )
        
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        
        logger.info(f"POST /projects - Created '{project_data.name}' (ID: {db_project.id})")
        
        return ProjectResponse.from_orm(db_project)
    
    except Exception as e:
        db.rollback()
        logger.error(f"POST /projects - Error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}"
        )


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project_info(
    project_id: int,
    project_update: ProjectUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ProjectResponse:
    """
    Update project information (owner only).
    
    Path Parameters:
    - project_id: The ID of the project
    
    Request Body:
    - name: New project name (optional)
    - description: New description (optional)
    - goal_amount: New goal amount (optional)
    - latitude: New latitude (optional)
    - longitude: New longitude (optional)
    
    Returns:
        Updated ProjectResponse
    
    Requires:
        Valid authentication token and project ownership
    """
    try:
        project = db.query(ProjectDB).filter(ProjectDB.id == project_id).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found"
            )
        
        if project.owner_id != current_user.id:
            logger.warning(f"PUT /projects/{project_id} - Unauthorized access")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only project owner can update this project"
            )
        
        if project_update.name is not None:
            project.name = project_update.name
        if project_update.description is not None:
            project.description = project_update.description
        if project_update.icon is not None:
            project.icon = project_update.icon
        if project_update.color is not None:
            project.color = project_update.color
        if project_update.goal_amount is not None:
            project.goal_amount = project_update.goal_amount
        if project_update.report_url is not None:
            project.report_url = project_update.report_url
        if project_update.latitude is not None:
            project.latitude = project_update.latitude
        if project_update.longitude is not None:
            project.longitude = project_update.longitude
        
        db.commit()
        db.refresh(project)
        
        logger.info(f"PUT /projects/{project_id} - Updated")
        
        return ProjectResponse.from_orm(project)
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"PUT /projects/{project_id} - Error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update project: {str(e)}"
        )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
) -> None:
    try:
        project = db.query(ProjectDB).filter(ProjectDB.id == project_id).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found"
            )
        
        if project.owner_id != current_user.id and not current_user.is_admin:
            logger.warning(f"DELETE /projects/{project_id} - Unauthorized access")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this project"
            )
        
        db.delete(project)
        db.commit()
        
        logger.info(f"DELETE /projects/{project_id} - Deleted")
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"DELETE /projects/{project_id} - Error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete project: {str(e)}"
        )
