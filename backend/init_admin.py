"""
Create preset users for the application
Run: python init_admin.py
"""

import sys
import os
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, init_db, engine, Base
from models import UserDB
import bcrypt

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def create_preset_users():
    """Create preset users for development/testing"""
    
    try:
        # Initialize database tables
        init_db()
        
        # Create session
        db = SessionLocal()
        
        # Clear existing users and projects
        db.query(UserDB).delete()
        db.commit()
        print("Cleared existing users")
        
        # Create developer account
        dev_email = "igel2020i@gmail.com"
        dev = db.query(UserDB).filter(UserDB.email == dev_email).first()
        
        if not dev:
            new_dev = UserDB(
                email=dev_email,
                name="Developer",
                password_hash=hash_password("1"),
                is_admin=False,
                role="Donor",
                avatar="👨‍💻",
                xp=0,
                rating_level="Bronze",
                is_banned=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(new_dev)
            db.commit()
            print(f"✓ Developer account created:")
            print(f"  Email: {dev_email}")
            print(f"  Password: 1")
            print(f"  Role: Donor")
        else:
            print(f"✓ Developer account already exists: {dev_email}")
        
        # Create admin account
        admin_email = "kurt20212022@gmail.com"
        admin = db.query(UserDB).filter(UserDB.email == admin_email).first()
        
        if not admin:
            new_admin = UserDB(
                email=admin_email,
                name="Admin",
                password_hash=hash_password("1"),
                is_admin=True,
                role="Administrator",
                avatar="🔐",
                xp=0,
                rating_level="Bronze",
                is_banned=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(new_admin)
            db.commit()
            print(f"✓ Admin account created:")
            print(f"  Email: {admin_email}")
            print(f"  Password: 1")
            print(f"  Role: Administrator")
        else:
            print(f"✓ Admin account already exists: {admin_email}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Initializing preset user accounts...\n")
    success = create_preset_users()
    print("\nDone!")
    exit(0 if success else 1)
