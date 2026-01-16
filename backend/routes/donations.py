"""
Routes for donations/orders management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from database import get_db
from routes.auth import get_current_user
from models import DonationDB, ProjectDB

router = APIRouter(prefix="/api/donations", tags=["donations"])


class AcceptOrderRequest(BaseModel):
    courierId: int


class DeclineOrderRequest(BaseModel):
    courierId: int


@router.get("")
async def get_donations(
    userId: Optional[int] = Query(None, description="Filter by user ID"),
    available: Optional[bool] = Query(None, description="Get available orders for couriers"),
    db: Session = Depends(get_db)
):
    """Get donations/orders"""
    if userId:
        # Получить донации конкретного пользователя (для донора)
        donations = db.query(DonationDB).filter(DonationDB.user_id == userId).all()
        result = []
        for donation in donations:
            result.append({
                "id": donation.id,
                "product_name": donation.project.name if donation.project else "Unknown",
                "name": donation.project.name if donation.project else "Unknown",
                "description": donation.project.description if donation.project else "",
                "status": "Активен",
                "created_at": donation.created_at.isoformat() if donation.created_at else None,
                "delivery_address": donation.project.address if donation.project and hasattr(donation.project, 'address') else None,
                "thumb_url": donation.project.thumb_url if donation.project and hasattr(donation.project, 'thumb_url') else None
            })
        return result
    elif available:
        # Получить все доступные заказы для доставщика (все донации)
        # Если донаций нет, возвращаем все проекты как доступные заказы
        donations = db.query(DonationDB).all()
        result = []
        for donation in donations:
            if donation.project:
                result.append({
                    "id": donation.id,
                    "product_name": donation.project.name,
                    "name": donation.project.name,
                    "description": donation.project.description or "",
                    "status": "Доступен",
                    "created_at": donation.created_at.isoformat() if donation.created_at else None,
                    "delivery_address": getattr(donation.project, 'address', None) or getattr(donation.project, 'location', None) or "",
                    "thumb_url": getattr(donation.project, 'thumb_url', None) or getattr(donation.project, 'image_url', None)
                })
        
        # Если донаций нет, возвращаем все проекты
        if not result:
            from models import ProjectDB
            projects = db.query(ProjectDB).all()
            for project in projects:
                result.append({
                    "id": project.id,
                    "product_name": project.name,
                    "name": project.name,
                    "description": project.description or "",
                    "status": "Доступен",
                    "created_at": project.created_at.isoformat() if hasattr(project, 'created_at') and project.created_at else None,
                    "delivery_address": getattr(project, 'address', None) or getattr(project, 'location', None) or "",
                    "thumb_url": getattr(project, 'thumb_url', None) or getattr(project, 'image_url', None)
                })
        
        return result
    else:
        # Получить все донации
        donations = db.query(DonationDB).all()
        result = []
        for donation in donations:
            result.append({
                "id": donation.id,
                "product_name": donation.project.name if donation.project else "Unknown",
                "name": donation.project.name if donation.project else "Unknown",
                "description": donation.project.description if donation.project else "",
                "status": "Активен",
                "created_at": donation.created_at.isoformat() if donation.created_at else None,
                "delivery_address": donation.project.address if donation.project and hasattr(donation.project, 'address') else None,
                "thumb_url": donation.project.thumb_url if donation.project and hasattr(donation.project, 'thumb_url') else None
            })
        return result


class DonationCreateRequest(BaseModel):
    productName: str
    quantity: str
    expiryDate: str
    description: str
    deliveryAddress: str
    userId: int


@router.post("")
async def create_donation(
    request: DonationCreateRequest,
    db: Session = Depends(get_db)
):
    """Create a new donation/order"""
    # Создаем проект для этого заказа
    from models import ProjectDB, ProjectStatus
    from datetime import datetime
    
    project = ProjectDB(
        name=request.productName,
        description=request.description,
        goal_amount=1000,  # Default value
        current_amount=0,
        owner_id=request.userId,
        status=ProjectStatus.ACTIVE
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    
    # Создаем донацию
    donation = DonationDB(
        user_id=request.userId,
        project_id=project.id,
        amount=0  # Для продуктов это не денежная сумма
    )
    db.add(donation)
    db.commit()
    db.refresh(donation)
    
    return {
        "id": donation.id,
        "product_name": request.productName,
        "name": request.productName,
        "description": request.description,
        "status": "Активен",
        "created_at": donation.created_at.isoformat() if donation.created_at else None,
        "delivery_address": request.deliveryAddress,
        "thumb_url": None
    }


@router.delete("/{donation_id}")
async def delete_donation(
    donation_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a donation/order (only owner can delete)"""
    donation = db.query(DonationDB).filter(DonationDB.id == donation_id).first()
    
    if not donation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donation not found"
        )
    
    # Проверяем, что пользователь является владельцем
    if donation.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only donation owner or admin can delete"
        )
    
    db.delete(donation)
    db.commit()
    
    return {"message": "Donation deleted successfully"}


@router.post("/{donation_id}/accept")
async def accept_order(
    donation_id: int,
    request: AcceptOrderRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Accept an order by courier"""
    donation = db.query(DonationDB).filter(DonationDB.id == donation_id).first()
    
    if not donation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Здесь можно добавить логику обновления статуса заказа
    # Например, добавить поле courier_id в DonationDB или создать отдельную таблицу для отслеживания
    
    return {
        "message": "Order accepted successfully",
        "donation_id": donation_id,
        "courier_id": request.courierId
    }


@router.post("/{donation_id}/decline")
async def decline_order(
    donation_id: int,
    request: DeclineOrderRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Decline an order by courier"""
    donation = db.query(DonationDB).filter(DonationDB.id == donation_id).first()
    
    if not donation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Здесь можно добавить логику для отслеживания отклоненных заказов
    # Например, создать таблицу declined_orders для хранения истории
    
    return {
        "message": "Order declined successfully",
        "donation_id": donation_id,
        "courier_id": request.courierId
    }
