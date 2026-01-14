from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sys
import os

# Ensure backend directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import init_db, settings

# Import routers
from routes import auth, users, projects, issues, notifications, adminpanel, routing
from middleware.ban_middleware import BanCheckMiddleware
from services.routing_service import routing_service

# Initialize FastAPI app
app = FastAPI(
    title="Save Food API",
    description="Food charity distribution management system with transparency",
    version="2.0.0"
)

# Add middlewares (Ban check before CORS)
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


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and services on app startup"""
    init_db()
    print(f"SQLite3 database initialized (Environment: {settings.environment})")
    
    # Initialize routing service
    await routing_service.init_session()
    is_healthy = await routing_service.check_valhalla_health()
    if is_healthy:
        print("✓ Valhalla routing service is healthy")
    else:
        print("⚠ Valhalla routing service is not available (routing features will be limited)")


# Cleanup on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup services on app shutdown"""
    await routing_service.close_session()
    print("Routing service cleaned up")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "Save Food API v2.0.0 is running",
        "database": "SQLite3",
        "features": ["Transparent Charity", "Gamification", "Volunteer Matching"]
    }


@app.get("/")
async def root():
    """Root endpoint"""
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


# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(issues.router)
app.include_router(notifications.router)
app.include_router(adminpanel.router)
app.include_router(routing.router)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle all exceptions"""
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
