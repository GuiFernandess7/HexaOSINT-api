from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from database.session import get_db
from auth.schemas import (
    UserCreate, UserLogin, Token, UserResponse, 
    RefreshTokenRequest, LogoutRequest
)
from auth.auth_service import AuthService
from auth.config import get_current_active_user
from database.models.db_models import User
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

router = APIRouter(prefix="/auth", tags=["authentication"])

limiter = Limiter(key_func=get_remote_address)

def get_login_key(request: Request):
    ip_address = get_remote_address(request)
    
    try:
        return f"login:{ip_address}"
    except:
        return f"login:{ip_address}"


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("3 per minute")
def register_user(request: Request, user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    try:
        auth_service = AuthService(db)
        user = auth_service.create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/login", response_model=Token)
@limiter.limit("5 per minute", key_func=get_login_key)
def login_user(login_data: UserLogin, request: Request, db: Session = Depends(get_db)):
    """Login user and return JWT token."""
    try:
        auth_service = AuthService(db)
        user = auth_service.authenticate_user(login_data.email, login_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token = auth_service.create_access_token(user)
        
        refresh_token = auth_service.generate_refresh_token(
            user, 
            device_info=request.headers.get("User-Agent"),
            ip_address=request.client.host if request.client else None
        )
        
        return {
            "message": "Login successful.",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 86400, 
            "user": user
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return current_user


@router.get("/verify-token")
def verify_token(current_user: User = Depends(get_current_active_user)):
    """Verify if the current token is valid."""
    return {"message": "Token is valid", "user_id": current_user.user_id}


@router.post("/refresh", response_model=Token)
@limiter.limit("10 per minute")
def refresh_token(
    refresh_request: RefreshTokenRequest, 
    request: Request,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token."""
    try:
        auth_service = AuthService(db)
        user = auth_service.verify_refresh_token(refresh_request.refresh_token)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
                headers={"X-User-JWT": "Invalid"},
            )
        
        new_access_token = auth_service.create_access_token(user)
        
        new_refresh_token = auth_service.generate_refresh_token(
            user,
            device_info=request.headers.get("User-Agent"),
            ip_address=request.client.host if request.client else None
        )
        
        auth_service.revoke_refresh_token(refresh_request.refresh_token)
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": 86400,  
            "user": user
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/logout")
def logout(
    logout_request: LogoutRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Logout user and revoke tokens."""
    try:
        auth_service = AuthService(db)
        
        if logout_request.refresh_token:
            success = auth_service.revoke_refresh_token(logout_request.refresh_token)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid refresh token"
                )
            return {"message": "Logged out successfully"}
        
        revoked_count = auth_service.revoke_all_user_tokens(current_user.user_id)
        return {
            "message": "Logged out successfully",
            "revoked_tokens": revoked_count
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
