"""Database seed script to populate test data"""

from database import SessionLocal, engine, Base
from models import UserDB, ProjectDB
from auth import hash_password
import crud


def seed_database():
    """Populate database with test data"""
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if test user already exists
        existing_user = crud.get_user_by_email(db, "donor@example.com")
        if existing_user:
            print("[OK] Test user already exists")
            user_id = existing_user.id
        else:
            # Create test user
            test_user = UserDB(
                email="donor@example.com",
                name="Test User",
                password_hash=hash_password("password123"),
                role="Donor",  # Set role to Donor
                avatar="👤",
                xp=0,
                rating_level="Bronze",
                is_admin=False
            )
            
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            user_id = test_user.id
            
            print("[OK] Test user created successfully")
            print(f"  Email: donor@example.com")
            print(f"  Password: password123")
            print(f"  User ID: {user_id}")
        
        # Check if sample projects exist
        existing_projects = db.query(ProjectDB).filter(ProjectDB.owner_id == user_id).count()
        if existing_projects > 0:
            print(f"[OK] Sample projects already exist ({existing_projects} projects)")
            return
        
        # Create sample projects across Russia
        projects_data = [
            # Moscow projects
            {
                "name": "Moscow Food Distribution",
                "description": "Distribute food to local communities in Moscow",
                "icon": "🍕",
                "color": "#ef4444",
                "goal_amount": 5000.0,
                "owner_id": user_id,
                "latitude": 55.7558,
                "longitude": 37.6173
            },
            {
                "name": "Moscow School Meals",
                "description": "Provide nutritious meals to school children in Moscow",
                "icon": "🍎",
                "color": "#10b981",
                "goal_amount": 10000.0,
                "owner_id": user_id,
                "latitude": 55.7505,
                "longitude": 37.6175
            },
            # St. Petersburg projects
            {
                "name": "St. Petersburg Elderly Care",
                "description": "Home-delivered meals for elderly residents in SPb",
                "icon": "🥗",
                "color": "#6b7280",
                "goal_amount": 7500.0,
                "owner_id": user_id,
                "latitude": 59.9311,
                "longitude": 30.3609
            },
            {
                "name": "St. Petersburg Emergency Relief",
                "description": "Rapid response food distribution in St. Petersburg",
                "icon": "🚨",
                "color": "#f59e0b",
                "goal_amount": 15000.0,
                "owner_id": user_id,
                "latitude": 59.8311,
                "longitude": 30.4609
            },
            # Yekaterinburg projects
            {
                "name": "Yekaterinburg Community Kitchen",
                "description": "Community food distribution in Yekaterinburg",
                "icon": "🍲",
                "color": "#3b82f6",
                "goal_amount": 8000.0,
                "owner_id": user_id,
                "latitude": 56.8389,
                "longitude": 60.6057
            },
            {
                "name": "Yekaterinburg Children's Meals",
                "description": "Nutritious meals for underprivileged children",
                "icon": "👨‍👩‍👧‍👦",
                "color": "#ec4899",
                "goal_amount": 6000.0,
                "owner_id": user_id,
                "latitude": 56.8500,
                "longitude": 60.6100
            },
            # Novosibirsk projects
            {
                "name": "Novosibirsk Food Bank",
                "description": "Food bank and distribution center in Novosibirsk",
                "icon": "🏦",
                "color": "#8b5cf6",
                "goal_amount": 9000.0,
                "owner_id": user_id,
                "latitude": 55.0415,
                "longitude": 82.9346
            },
            {
                "name": "Novosibirsk Homeless Support",
                "description": "Daily meals for homeless and vulnerable people",
                "icon": "❤️",
                "color": "#ef4444",
                "goal_amount": 12000.0,
                "owner_id": user_id,
                "latitude": 55.0500,
                "longitude": 82.9400
            },
            # Kazan projects
            {
                "name": "Kazan Family Assistance",
                "description": "Food assistance for large families in Kazan",
                "icon": "👪",
                "color": "#14b8a6",
                "goal_amount": 5500.0,
                "owner_id": user_id,
                "latitude": 55.7887,
                "longitude": 49.1221
            },
            {
                "name": "Kazan Student Support",
                "description": "Affordable meals for students in Kazan",
                "icon": "📚",
                "color": "#f97316",
                "goal_amount": 4000.0,
                "owner_id": user_id,
                "latitude": 55.7950,
                "longitude": 49.1280
            },
        ]
        
        for project_data in projects_data:
            project = ProjectDB(**project_data)
            db.add(project)
        
        db.commit()
        print(f"[OK] {len(projects_data)} sample projects created successfully")
        
    except Exception as e:
        print(f"[ERROR] Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
