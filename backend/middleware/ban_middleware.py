"""Middleware for checking banned users"""

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException, status
from sqlalchemy.orm import Session
from database import SessionLocal
from models import UserDB


class BanCheckMiddleware(BaseHTTPMiddleware):
    """Middleware to block banned users from accessing the API"""
    
    async def dispatch(self, request: Request, call_next):
        # Skip check for public endpoints
        public_paths = [
            "/docs",
            "/openapi.json",
            "/health",
            "/api/auth/login",
            "/api/auth/register",
            "/api/auth/refresh",
            "/redoc"
        ]
        
        if any(request.url.path.startswith(path) for path in public_paths):
            return await call_next(request)
        
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                token = auth_header.split(" ")[1]
                
                # Parse token to get user_id
                from routes.auth import verify_token
                payload = verify_token(token)
                
                if payload and "sub" in payload:
                    user_id = int(payload["sub"])
                    db = SessionLocal()
                    try:
                        user = db.query(UserDB).filter(UserDB.id == user_id).first()
                        
                        if user and user.is_banned:
                            raise HTTPException(
                                status_code=status.HTTP_403_FORBIDDEN,
                                detail="User account is banned"
                            )
                    finally:
                        db.close()
            except HTTPException:
                raise
            except Exception as e:
                # Log but don't block - let normal auth handling take care
                pass
        
        return await call_next(request)
