import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import UserDB, ProjectDB, DeliveryDB, UserRole
from auth import hash_password
from datetime import datetime

def seed_all():
    db = SessionLocal()
    try:
        donor = UserDB(
            email="donor@test.com",
            name="Test Donor",
            password_hash=hash_password("password123"),
            role=UserRole.DONOR,
            courier_deliveries=0,
            courier_rating=5.0,
            courier_avg_delivery_time=0.0
        )
        db.add(donor)
        db.commit()
        db.refresh(donor)
        print(f"Created donor: {donor.email}")
        
        courier = UserDB(
            email="courier@test.com",
            name="Test Courier",
            password_hash=hash_password("password123"),
            role=UserRole.COURIER,
            courier_deliveries=0,
            courier_rating=5.0,
            courier_avg_delivery_time=0.0
        )
        db.add(courier)
        db.commit()
        db.refresh(courier)
        print(f"Created courier: {courier.email}")
        
        projects = [
            ProjectDB(
                name="Bread Donation",
                description="Fresh bread ready for delivery",
                owner_id=donor.id,
                goal_amount=100,
                current_amount=100,
                latitude=55.7536,
                longitude=37.6201,
                status="Active"
            ),
            ProjectDB(
                name="Vegetables Pack",
                description="Assorted vegetables from local farm",
                owner_id=donor.id,
                goal_amount=100,
                current_amount=100,
                latitude=55.7480,
                longitude=37.6300,
                status="Active"
            ),
            ProjectDB(
                name="Canned Food",
                description="Various canned food items",
                owner_id=donor.id,
                goal_amount=100,
                current_amount=100,
                latitude=55.7620,
                longitude=37.6150,
                status="Active"
            ),
        ]
        
        for project in projects:
            db.add(project)
        
        db.commit()
        print(f"Created {len(projects)} projects")
        
        for project in projects:
            db.refresh(project)
            delivery = DeliveryDB(
                project_id=project.id,
                status="pending",
                created_at=datetime.utcnow()
            )
            db.add(delivery)
        
        db.commit()
        deliveries = db.query(DeliveryDB).all()
        print(f"Created {len(deliveries)} deliveries")
        
        for delivery in deliveries:
            print(f"  - Delivery {delivery.id}: Project {delivery.project_id}, Status: {delivery.status}")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_all()
