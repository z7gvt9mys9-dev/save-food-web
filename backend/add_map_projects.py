# -*- coding: utf-8 -*-
"""Add map projects"""

from database import SessionLocal
from models import ProjectDB, UserDB, ProjectStatus

db = SessionLocal()

developer = db.query(UserDB).filter(UserDB.name == "Developer").first()
if not developer:
    print("Developer not found")
    db.close()
    exit(1)

projects = [
    {
        "name": "Food Distribution Taganskaya",
        "description": "Children food collection and distribution",
        "icon": "🍼",
        "goal_amount": 50000,
        "current_amount": 20000,
        "latitude": 55.7558,
        "longitude": 37.6173,
    },
    {
        "name": "Hot Meals Krasnaya Presnya",
        "description": "Hot meals and drinks for those in need",
        "icon": "🍽️",
        "goal_amount": 75000,
        "current_amount": 30000,
        "latitude": 55.7836,
        "longitude": 37.6299,
    },
    {
        "name": "Fresh Produce Semenovskaya",
        "description": "Fresh fruits and vegetables from farmers",
        "icon": "🥕",
        "goal_amount": 60000,
        "current_amount": 25000,
        "latitude": 55.7639,
        "longitude": 37.7211,
    },
    {
        "name": "Bread and Bakes Basmanny",
        "description": "Fresh bread every day",
        "icon": "🍞",
        "goal_amount": 40000,
        "current_amount": 15000,
        "latitude": 55.7626,
        "longitude": 37.6274,
    },
    {
        "name": "Dairy Products Meshchansky",
        "description": "Milk and yogurt for social institutions",
        "icon": "🥛",
        "goal_amount": 55000,
        "current_amount": 22000,
        "latitude": 55.7914,
        "longitude": 37.6318,
    },
]

added = 0
for p in projects:
    existing = db.query(ProjectDB).filter(ProjectDB.name == p["name"]).first()
    if existing:
        print(f"[SKIP] {p['name']}")
        continue
    
    proj = ProjectDB(
        name=p["name"],
        description=p["description"],
        icon=p["icon"],
        goal_amount=p["goal_amount"],
        current_amount=p["current_amount"],
        latitude=p["latitude"],
        longitude=p["longitude"],
        owner_id=developer.id,
        status=ProjectStatus.ACTIVE,
        is_verified=True
    )
    db.add(proj)
    added += 1
    print(f"[ADD] {p['name']}")

db.commit()
print(f"\nAdded {added} projects")

all_projects = db.query(ProjectDB).all()
print(f"Total projects: {len(all_projects)}")

db.close()
