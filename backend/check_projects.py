#!/usr/bin/env python3

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, settings
from models import ProjectDB, UserDB
import json

def check_and_seed_projects():
    db = SessionLocal()
    
    try:
        projects = db.query(ProjectDB).all()
        print(f"\n{'='*60}")
        print(f"Current projects in database: {len(projects)}")
        print(f"{'='*60}\n")
        
        if projects:
            for i, project in enumerate(projects, 1):
                print(f"{i}. {project.name}")
                print(f"   ID: {project.id}")
                print(f"   Description: {project.description}")
                print(f"   Location: ({project.latitude}, {project.longitude})")
                print(f"   Goal: ${project.goal_amount} | Current: ${project.current_amount}")
                print(f"   Verified: {project.is_verified}")
                print()
        else:
            print("No projects found in database!")
            print("\nDo you want to add test projects? (y/n): ", end="")
            response = input().lower().strip()
            
            if response == 'y':
                admin = db.query(UserDB).filter(UserDB.is_admin == True).first()
                
                if not admin:
                    print("\nNo admin user found. Creating test admin user...")
                    from auth import hash_password
                    test_admin = UserDB(
                        email="admin@savefood.local",
                        name="System Admin",
                        password_hash=hash_password("admin123"),
                        is_admin=True,
                        role="Administrator"
                    )
                    db.add(test_admin)
                    db.commit()
                    db.refresh(test_admin)
                    print(f"Admin user created (ID: {test_admin.id})")
                    admin = test_admin
                
                test_projects = [
                    {
                        "name": "Bakery Donation",
                        "description": "Distributing bread and buns to those in need",
                        "icon": "bread",
                        "color": "#D4A574",
                        "goal_amount": 5000.0,
                        "latitude": 55.7536,
                        "longitude": 37.6201,
                        "is_verified": True
                    },
                    {
                        "name": "Charity Canteen",
                        "description": "Free meals for low-income citizens",
                        "icon": "food",
                        "color": "#FF6B6B",
                        "goal_amount": 10000.0,
                        "latitude": 55.7596,
                        "longitude": 37.6150,
                        "is_verified": True
                    },
                    {
                        "name": "Dairy Shop",
                        "description": "Milk product distribution",
                        "icon": "milk",
                        "color": "#95E1D3",
                        "goal_amount": 3000.0,
                        "latitude": 55.7466,
                        "longitude": 37.6261,
                        "is_verified": False
                    },
                    {
                        "name": "Vegetable Garden",
                        "description": "Fresh vegetables and fruits distribution",
                        "icon": "vegetables",
                        "color": "#38A169",
                        "goal_amount": 7000.0,
                        "latitude": 55.7606,
                        "longitude": 37.5950,
                        "is_verified": True
                    },
                    {
                        "name": "Clothing Store",
                        "description": "Collection and distribution of clean clothes",
                        "icon": "clothes",
                        "color": "#9F7AEA",
                        "goal_amount": 2000.0,
                        "latitude": 55.7436,
                        "longitude": 37.6351,
                        "is_verified": False
                    }
                ]
                
                print(f"\nAdding {len(test_projects)} test projects...\n")
                
                for project_data in test_projects:
                    new_project = ProjectDB(
                        owner_id=admin.id,
                        name=project_data["name"],
                        description=project_data["description"],
                        icon=project_data["icon"],
                        color=project_data["color"],
                        goal_amount=project_data["goal_amount"],
                        current_amount=project_data["goal_amount"] * 0.6,
                        latitude=project_data["latitude"],
                        longitude=project_data["longitude"],
                        is_verified=project_data["is_verified"],
                        status="Active"
                    )
                    db.add(new_project)
                    print(f"Added: {project_data['name']}")
                
                db.commit()
                print(f"\nTest projects added successfully!")
                
                projects = db.query(ProjectDB).all()
                print(f"\nTotal projects now: {len(projects)}")
    
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    print(f"Database: {settings.database_url}")
    check_and_seed_projects()
