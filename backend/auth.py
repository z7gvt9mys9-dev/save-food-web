from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
import os

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET")
if not SECRET_KEY:
    raise ValueError("JWT_SECRET environment variable is not set. This is required for the app to run.")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days

# Password hashing
SALT_ROUNDS = 12

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    # Limit password to 72 bytes as per bcrypt spec
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt(rounds=SALT_ROUNDS)
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    try:
        plain_bytes = plain_password.encode('utf-8')[:72]
        return bcrypt.checkpw(plain_bytes, hashed_password.encode('utf-8'))
    except Exception as e:
        print(f"Error verifying password: {e}")
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        print(f"Token verification error: {e}")
        return None

# Example usage
if __name__ == "__main__":
    password = "my_secure_password"
    hashed_password = hash_password(password)
    print("Hashed Password:", hashed_password)

    is_verified = verify_password("my_secure_password", hashed_password)
    print("Password Verified:", is_verified)

    token = create_access_token({"sub": "user1"})
    print("Access Token:", token)

    payload = verify_token(token)
    print("Decoded Payload:", payload)
