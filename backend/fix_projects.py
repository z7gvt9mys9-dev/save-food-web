#!/usr/bin/env python3

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import ProjectDB

def fix_projects_coordinates():
    db = SessionLocal()
    
    try:
        projects_without_coords = db.query(ProjectDB).filter(
            (ProjectDB.latitude.is_(None)) | (ProjectDB.longitude.is_(None))
        ).all()
        
        print(f"\n{'='*60}")
        print(f"Found {len(projects_without_coords)} projects without coordinates")
        print(f"{'='*60}\n")
        
        moscow_coordinates = [
            (55.7536, 37.6201),
            (55.7596, 37.6150),
            (55.7466, 37.6261),
            (55.7606, 37.5950),
            (55.7436, 37.6351),
        ]
        
        for i, project in enumerate(projects_without_coords):
            lat, lon = moscow_coordinates[i % len(moscow_coordinates)]
            project.latitude = lat
            project.longitude = lon
            project.is_verified = True if i % 2 == 0 else False
            
            if project.current_amount == 0:
                project.current_amount = project.goal_amount * 0.5
            
            print(f"Updated: {project.name} ({project.id})")
            print(f"  Coordinates: ({lat}, {lon})")
            print(f"  Verified: {project.is_verified}")
            print()
        
        db.commit()
        print("Projects updated successfully!")
        
        all_projects = db.query(ProjectDB).all()
        print(f"\n{'='*60}")
        print(f"Final project list ({len(all_projects)} total):")
        print(f"{'='*60}\n")
        
        for i, project in enumerate(all_projects, 1):
            print(f"{i}. {project.name} (ID: {project.id})")
            print(f"   Location: ({project.latitude}, {project.longitude})")
            print(f"   Verified: {project.is_verified}")
            print()
    
    except Exception as e:
        print(f"Error: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_projects_coordinates()
