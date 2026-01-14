"""
Create first admin user via ORM
Run: python init_admin.py
"""

import sys
import os
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, init_db
from models import UserDB
import bcrypt

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def create_admin():
    """Create admin user using SQLAlchemy ORM"""
    
    try:
        # Initialize database tables
        init_db()
        
        # Create session
        db = SessionLocal()
        
        # Check if admin exists
        admin = db.query(UserDB).filter(UserDB.email == "k9x2m@sys.local").first()
        
        if admin:
            print("Admin already exists!")
            print(f"   Email: k9x2m@sys.local")
            db.close()
            return True
        
        # Create new admin user
        admin_password = "Tx7nP2!"
        new_admin = UserDB(
            email="k9x2m@sys.local",
            name="Admin User",
            password_hash=hash_password(admin_password),
            is_admin=True,
            role="Administrator",
            avatar="LOCK",
            xp=0,
            rating_level="Bronze",
            is_banned=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(new_admin)
        db.commit()
        
        print("Admin user created successfully!")
        print(f"   Email: admin@savefood.local")
        print(f"   Password: {admin_password}")
        print(f"   Role: Admin")
        print(f"   Database: savefood.db")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Creating first admin user...\n")
    success = create_admin()
    print("\nDone!")
    exit(0 if success else 1)
