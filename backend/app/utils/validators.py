"""
Input validation utilities
"""

from typing import Optional, Callable, Any
import re
from .errors import ValidationError


class ValidationRules:
    """Common validation rules"""
    
    MIN_PASSWORD_LENGTH = 6
    MAX_PASSWORD_LENGTH = 128
    MIN_EMAIL_LENGTH = 5
    MAX_EMAIL_LENGTH = 255
    MIN_NAME_LENGTH = 2
    MAX_NAME_LENGTH = 100
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')


class Validator:
    """Input validation helper"""
    
    @staticmethod
    def validate_email(email: str) -> str:
        """Validate email format and length"""
        if not email:
            raise ValidationError("Email is required")
        
        email = email.strip().lower()
        
        if len(email) < ValidationRules.MIN_EMAIL_LENGTH:
            raise ValidationError(f"Email must be at least {ValidationRules.MIN_EMAIL_LENGTH} characters")
        
        if len(email) > ValidationRules.MAX_EMAIL_LENGTH:
            raise ValidationError(f"Email cannot exceed {ValidationRules.MAX_EMAIL_LENGTH} characters")
        
        if not ValidationRules.EMAIL_REGEX.match(email):
            raise ValidationError("Invalid email format")
        
        return email
    
    @staticmethod
    def validate_password(password: str) -> str:
        """Validate password strength"""
        if not password:
            raise ValidationError("Password is required")
        
        if len(password) < ValidationRules.MIN_PASSWORD_LENGTH:
            raise ValidationError(
                f"Password must be at least {ValidationRules.MIN_PASSWORD_LENGTH} characters"
            )
        
        if len(password) > ValidationRules.MAX_PASSWORD_LENGTH:
            raise ValidationError(
                f"Password cannot exceed {ValidationRules.MAX_PASSWORD_LENGTH} characters"
            )
        
        return password
    
    @staticmethod
    def validate_name(name: str, field_name: str = "Name") -> str:
        """Validate name field"""
        if not name:
            raise ValidationError(f"{field_name} is required")
        
        name = name.strip()
        
        if len(name) < ValidationRules.MIN_NAME_LENGTH:
            raise ValidationError(
                f"{field_name} must be at least {ValidationRules.MIN_NAME_LENGTH} characters"
            )
        
        if len(name) > ValidationRules.MAX_NAME_LENGTH:
            raise ValidationError(
                f"{field_name} cannot exceed {ValidationRules.MAX_NAME_LENGTH} characters"
            )
        
        return name
    
    @staticmethod
    def validate_string(
        value: str,
        field_name: str,
        min_length: int = 1,
        max_length: int = 500,
        required: bool = True,
    ) -> str:
        """Generic string validation"""
        if not value:
            if required:
                raise ValidationError(f"{field_name} is required")
            return ""
        
        value = value.strip()
        
        if len(value) < min_length:
            raise ValidationError(
                f"{field_name} must be at least {min_length} characters"
            )
        
        if len(value) > max_length:
            raise ValidationError(
                f"{field_name} cannot exceed {max_length} characters"
            )
        
        return value
    
    @staticmethod
    def validate_integer(
        value: Any,
        field_name: str,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
    ) -> int:
        """Validate integer value"""
        try:
            int_value = int(value)
        except (TypeError, ValueError):
            raise ValidationError(f"{field_name} must be an integer")
        
        if min_value is not None and int_value < min_value:
            raise ValidationError(
                f"{field_name} must be at least {min_value}"
            )
        
        if max_value is not None and int_value > max_value:
            raise ValidationError(
                f"{field_name} cannot exceed {max_value}"
            )
        
        return int_value
    
    @staticmethod
    def validate_enum(value: str, field_name: str, allowed_values: list) -> str:
        """Validate enum value"""
        if value not in allowed_values:
            raise ValidationError(
                f"Invalid {field_name}. Must be one of: {', '.join(allowed_values)}"
            )
        
        return value
    
    @staticmethod
    def validate_not_empty(value: Any, field_name: str) -> Any:
        """Validate that value is not empty"""
        if not value:
            raise ValidationError(f"{field_name} cannot be empty")
        
        return value
