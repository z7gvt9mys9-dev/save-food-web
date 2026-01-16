from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from database import get_db
from routes.auth import get_current_user
from models import DeliveryResponse, DeliveryDetailResponse, UserResponse, ProjectResponse
import crud

router = APIRouter(prefix="/api/deliveries", tags=["deliveries"])


class AcceptDeliveryRequest(BaseModel):
    delivery_id: int


class CompleteDeliveryRequest(BaseModel):
    delivery_id: int
    delivery_time_minutes: int
    rating: float


@router.get("", response_model=List[DeliveryDetailResponse])
async def get_all_pending_deliveries(db: Session = Depends(get_db)):
    deliveries = crud.get_all_pending_deliveries(db)
    return deliveries


@router.post("/accept", response_model=DeliveryDetailResponse)
async def accept_delivery(
    request: AcceptDeliveryRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    delivery = crud.get_delivery_by_id(db, request.delivery_id)
    
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery not found"
        )
    
    if delivery.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Delivery is not available"
        )
    
    updated_delivery = crud.accept_delivery(db, request.delivery_id, current_user.id)
    return updated_delivery


@router.post("/complete", response_model=DeliveryDetailResponse)
async def complete_delivery(
    request: CompleteDeliveryRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    delivery = crud.get_delivery_by_id(db, request.delivery_id)
    
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery not found"
        )
    
    if delivery.courier_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not assigned to this delivery"
        )
    
    updated_delivery = crud.complete_delivery(
        db,
        request.delivery_id,
        request.delivery_time_minutes,
        request.rating
    )
    return updated_delivery
