#!/usr/bin/env python3

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import ProjectDB

def clear_projects():
    db = SessionLocal()
    
    try:
        count = db.query(ProjectDB).count()
        print(f"\n{'='*60}")
        print(f"Clearing projects from database...")
        print(f"Found {count} projects to delete")
        print(f"{'='*60}\n")
        
        if count == 0:
            print("Database is already empty - no projects to delete")
            return
        
        projects = db.query(ProjectDB).all()
        print("Projects to be deleted:")
        for i, project in enumerate(projects, 1):
            print(f"  {i}. {project.name} (ID: {project.id})")
        print()
        
        response = input("Are you sure you want to delete ALL projects? (yes/no): ").lower().strip()
        
        if response != 'yes':
            print("Deletion cancelled")
            return
        
        db.query(ProjectDB).delete()
        db.commit()
        
        remaining = db.query(ProjectDB).count()
        print(f"\nSuccessfully deleted {count} projects!")
        print(f"Remaining projects in database: {remaining}")
        print(f"{'='*60}\n")
        
    except Exception as e:
        db.rollback()
        print(f"\nError: {str(e)}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    clear_projects()
