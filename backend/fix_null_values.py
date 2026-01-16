#!/usr/bin/env python3

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import ProjectDB

def fix_null_values():
    db = SessionLocal()
    
    try:
        projects_no_icon = db.query(ProjectDB).filter(ProjectDB.icon.is_(None)).all()
        for project in projects_no_icon:
            project.icon = "box"
            print(f"Fixed icon for {project.name}")
        
        projects_no_color = db.query(ProjectDB).filter(ProjectDB.color.is_(None)).all()
        for project in projects_no_color:
            project.color = "#6b7280"
            print(f"Fixed color for {project.name}")
        
        projects_no_verified = db.query(ProjectDB).filter(ProjectDB.is_verified.is_(None)).all()
        for project in projects_no_verified:
            project.is_verified = False
            print(f"Fixed is_verified for {project.name}")
        
        db.commit()
        print("\nAll NULL values fixed successfully!")
        
        all_projects = db.query(ProjectDB).all()
        print(f"\n{'='*60}")
        print(f"Final project list ({len(all_projects)} total):")
        print(f"{'='*60}\n")
        
        for i, project in enumerate(all_projects, 1):
            print(f"{i}. {project.name} (ID: {project.id})")
            print(f"   Icon: {project.icon}")
            print(f"   Color: {project.color}")
            print(f"   Verified: {project.is_verified}")
            print()
    
    except Exception as e:
        print(f"Error: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_null_values()
