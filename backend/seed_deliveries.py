import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import DeliveryDB, ProjectDB
from datetime import datetime

def seed_deliveries():
    db = SessionLocal()
    try:
        projects = db.query(ProjectDB).filter(ProjectDB.owner_id != None).limit(10).all()
        
        if not projects:
            print("No projects found to create deliveries")
            return
        
        existing_deliveries = db.query(DeliveryDB).count()
        print(f"Existing deliveries: {existing_deliveries}")
        
        for project in projects:
            existing = db.query(DeliveryDB).filter(DeliveryDB.project_id == project.id).first()
            if not existing:
                delivery = DeliveryDB(
                    project_id=project.id,
                    status="pending",
                    created_at=datetime.utcnow()
                )
                db.add(delivery)
        
        db.commit()
        print(f"Deliveries created successfully")
        
        deliveries = db.query(DeliveryDB).all()
        print(f"Total deliveries in DB: {len(deliveries)}")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_deliveries()
