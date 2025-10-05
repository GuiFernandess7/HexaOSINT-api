from fastapi import FastAPI, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
import jwt
import dotenv
import os
import uuid
from typing import Optional
from database.session import get_session, get_db
from database.models.db_models import User
from auth.schemas import TokenData

dotenv.load_dotenv()

SECRET_KEY = os.getenv("SECRET_AUTH_KEY")


def verify_jwt(x_user_jwt: str = Header(..., alias="X-User-JWT")) -> dict:
    """Verify JWT token from custom header and return payload."""
    if not x_user_jwt:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-User-JWT header is required",
            headers={"X-User-JWT": "Required"},
        )
    
    try:
        payload = jwt.decode(x_user_jwt, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Expired token",
            headers={"X-User-JWT": "Invalid"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid token",
            headers={"X-User-JWT": "Invalid"},
        )


def get_current_user(
    payload: dict = Depends(verify_jwt),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token."""
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.user_id == user_uuid).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current admin user."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
