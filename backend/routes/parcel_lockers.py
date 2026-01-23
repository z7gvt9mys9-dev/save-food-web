from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from crud import (
    get_all_parcel_lockers, get_parcel_locker_by_id, create_parcel_locker,
    deactivate_parcel_locker
)
from models import ParcelLockerResponse, MessageResponse, ErrorResponse
from services.auth_service import get_current_user

router = APIRouter(prefix="/api/parcel-lockers", tags=["parcel-lockers"])


@router.get("", response_model=list[ParcelLockerResponse])
def get_parcel_lockers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all active parcel lockers"""
    lockers = get_all_parcel_lockers(db, skip=skip, limit=limit)
    
    result = []
    for locker in lockers:
        result.append({
            "id": locker.id,
            "name": locker.name,
            "address": locker.address,
            "latitude": locker.latitude,
            "longitude": locker.longitude,
            "total_capacity": locker.total_capacity,
            "current_occupancy": locker.current_occupancy,
            "is_active": locker.is_active,
            "available_slots": locker.total_capacity - locker.current_occupancy,
            "created_at": locker.created_at,
            "updated_at": locker.updated_at
        })
    
    return result


@router.get("/{locker_id}", response_model=ParcelLockerResponse)
def get_locker_details(locker_id: int, db: Session = Depends(get_db)):
    """Get parcel locker details by ID"""
    locker = get_parcel_locker_by_id(db, locker_id)
    if not locker:
        raise HTTPException(status_code=404, detail="Почтомат не найден")
    
    return {
        "id": locker.id,
        "name": locker.name,
        "address": locker.address,
        "latitude": locker.latitude,
        "longitude": locker.longitude,
        "total_capacity": locker.total_capacity,
        "current_occupancy": locker.current_occupancy,
        "is_active": locker.is_active,
        "available_slots": locker.total_capacity - locker.current_occupancy,
        "created_at": locker.created_at,
        "updated_at": locker.updated_at
    }


@router.post("/{locker_id}/deactivate", response_model=MessageResponse)
def deactivate_locker(
    locker_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Deactivate parcel locker (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Только администратор может отключать почтоматы")
    
    locker = deactivate_parcel_locker(db, locker_id, current_user.id)
    if not locker:
        raise HTTPException(status_code=404, detail="Почтомат не найден")
    
    return {"message": f"Почтомат '{locker.name}' отключен"}
