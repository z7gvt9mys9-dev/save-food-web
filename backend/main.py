from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import init_db, settings, SessionLocal
from models import UserDB
from routes import auth, users, projects, issues, notifications, adminpanel, routing, donations, deliveries
from middleware.ban_middleware import BanCheckMiddleware
from services.routing_service import routing_service
import bcrypt
app = FastAPI(
    title="Save Food API",
    description="Food charity distribution management system with transparency",
    version="2.0.0"
)

app.add_middleware(BanCheckMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://localhost:5000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def init_preset_users():
    """Initialize preset user accounts"""
    try:
        db = SessionLocal()
        
        preset_accounts = [
            {
                "email": "igel2020i@gmail.com",
                "name": "Developer",
                "password": "1",
                "role": "Donor",
                "avatar": "👨‍💻",
                "is_admin": False
            },
            {
                "email": "kurt20212022@gmail.com",
                "name": "Admin",
                "password": "1",
                "role": "Administrator",
                "avatar": "🔐",
                "is_admin": True
            }
        ]
        
        for account in preset_accounts:
            existing = db.query(UserDB).filter(UserDB.email == account["email"]).first()
            if not existing:
                new_user = UserDB(
                    email=account["email"],
                    name=account["name"],
                    password_hash=hash_password(account["password"]),
                    is_admin=account["is_admin"],
                    role=account["role"],
                    avatar=account["avatar"],
                    xp=0,
                    rating_level="Bronze",
                    is_banned=False,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(new_user)
                db.commit()
        
        db.close()
    except Exception as e:
        print(f"Warning: Could not initialize preset users: {e}")


@app.on_event("startup")
async def startup_event():
    init_db()
    print(f"SQLite3 database initialized (Environment: {settings.environment})")
    init_preset_users()
    await routing_service.init_session()
    is_healthy = await routing_service.check_valhalla_health()
    if is_healthy:
        print("Valhalla routing service is healthy")
    else:
        print("Valhalla routing service is not available")

@app.on_event("shutdown")
async def shutdown_event():
    await routing_service.close_session()
    print("Routing service cleaned up")


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "message": "Save Food API v2.0.0 is running",
        "database": "SQLite3",
        "features": ["Transparent Charity", "Gamification", "Volunteer Matching"]
    }

@app.get("/")
async def root():
    return {
        "message": "Welcome to Save Food API v2.0.0",
        "version": "2.0.0",
        "docs": "/docs",
        "features": {
            "charity": "Transparent donation tracking",
            "gamification": "XP and rating system for volunteers",
            "mapping": "Geolocation-based project discovery"
        },
        "endpoints": {
            "auth": "/api/auth",
            "users": "/api/users",
            "projects": "/api/projects",
            "issues": "/api/issues",
            "donations": "/api/donations",
            "notifications": "/api/notifications"
        }
    }

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(issues.router)
app.include_router(notifications.router)
app.include_router(adminpanel.router)
app.include_router(routing.router)
app.include_router(donations.router)
app.include_router(deliveries.router)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn
    
    port = settings.port
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
