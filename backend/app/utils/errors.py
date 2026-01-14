"""
Standardized error handling for the application
"""

from typing import Optional, Any, Dict
from enum import Enum


class ErrorType(str, Enum):
    """Standard error types for API responses"""
    VALIDATION_ERROR = "validation_error"
    AUTHENTICATION_ERROR = "authentication_error"
    AUTHORIZATION_ERROR = "authorization_error"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"
    INTERNAL_ERROR = "internal_error"
    EXTERNAL_SERVICE_ERROR = "external_service_error"


class AppError(Exception):
    """Base exception for application errors"""
    
    def __init__(
        self,
        message: str,
        error_type: ErrorType = ErrorType.INTERNAL_ERROR,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.error_type = error_type
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to API response format"""
        return {
            "status": "error",
            "type": self.error_type,
            "message": self.message,
            "details": self.details,
        }


class ValidationError(AppError):
    """Raised when input validation fails"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message,
            error_type=ErrorType.VALIDATION_ERROR,
            status_code=400,
            details=details,
        )


class AuthenticationError(AppError):
    """Raised when authentication fails"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message,
            error_type=ErrorType.AUTHENTICATION_ERROR,
            status_code=401,
        )


class AuthorizationError(AppError):
    """Raised when user lacks required permissions"""
    
    def __init__(self, message: str = "You don't have permission to access this resource"):
        super().__init__(
            message,
            error_type=ErrorType.AUTHORIZATION_ERROR,
            status_code=403,
        )


class NotFoundError(AppError):
    """Raised when a resource is not found"""
    
    def __init__(self, resource: str = "Resource"):
        super().__init__(
            f"{resource} not found",
            error_type=ErrorType.NOT_FOUND,
            status_code=404,
        )


class ConflictError(AppError):
    """Raised when a resource already exists"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message,
            error_type=ErrorType.CONFLICT,
            status_code=409,
            details=details,
        )


class ExternalServiceError(AppError):
    """Raised when external service fails"""
    
    def __init__(self, service: str, message: str = ""):
        msg = f"Error communicating with {service}"
        if message:
            msg += f": {message}"
        super().__init__(
            msg,
            error_type=ErrorType.EXTERNAL_SERVICE_ERROR,
            status_code=502,
        )
