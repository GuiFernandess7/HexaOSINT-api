import uuid
import secrets
from datetime import datetime, timedelta
from typing import Optional
import jwt
import bcrypt
from sqlalchemy.orm import Session
from database.models.db_models import User, RefreshToken
from auth.schemas import UserCreate, UserLogin, TokenData
from settings import settings


class AuthService:
    """Service for handling user authentication and authorization."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return bcrypt.checkpw(
            plain_password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )
    
    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        existing_user = self.db.query(User).filter(
            User.email == user_data.email
        ).first()
        
        if existing_user:
            raise ValueError("User already exists with this email.")
        

        hashed_password = self.hash_password(user_data.password)
        
        db_user = User(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            email=user_data.email,
            hashed_password=hashed_password,
            is_active=True,
            is_admin=False
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user with email and password."""
        user = self.db.query(User).filter(User.email == email).first()
        
        if not user:
            return None
        
        if not self.verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            return None
        
        user.last_login = datetime.utcnow()
        self.db.commit()
        
        return user
    
    def create_access_token(self, user: User, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=24) 
        
        to_encode = {
            "sub": str(user.user_id),
            "email": user.email,
            "is_admin": user.is_admin,
            "exp": expire
        }
        
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_AUTH_KEY, algorithm="HS256")
        return encoded_jwt
    
    def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Get a user by their ID."""
        return self.db.query(User).filter(User.user_id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by their email."""
        return self.db.query(User).filter(User.email == email).first()
    
    def update_user_last_login(self, user_id: uuid.UUID):
        """Update the last login timestamp for a user."""
        user = self.get_user_by_id(user_id)
        if user:
            user.last_login = datetime.utcnow()
            self.db.commit()
    
    def generate_refresh_token(self, user: User, device_info: Optional[str] = None, ip_address: Optional[str] = None) -> str:
        """Generate a new refresh token for the user."""
        refresh_token = secrets.token_urlsafe(64)
        
        expires_at = datetime.utcnow() + timedelta(days=30)
        
        db_refresh_token = RefreshToken(
            user_id=user.user_id,
            token=refresh_token,
            expires_at=expires_at,
            device_info=device_info,
            ip_address=ip_address
        )
        
        self.db.add(db_refresh_token)
        self.db.commit()
        
        return refresh_token
    
    def verify_refresh_token(self, refresh_token: str) -> Optional[User]:
        """Verify a refresh token and return the associated user."""
        db_token = self.db.query(RefreshToken).filter(
            RefreshToken.token == refresh_token,
            RefreshToken.is_revoked == False,
            RefreshToken.expires_at > datetime.utcnow()
        ).first()
        
        if not db_token:
            return None
        
        return db_token.user
    
    def revoke_refresh_token(self, refresh_token: str) -> bool:
        """Revoke a refresh token."""
        db_token = self.db.query(RefreshToken).filter(
            RefreshToken.token == refresh_token
        ).first()
        
        if not db_token:
            return False
        
        db_token.is_revoked = True
        db_token.revoked_at = datetime.utcnow()
        self.db.commit()
        
        return True
    
    def revoke_all_user_tokens(self, user_id: uuid.UUID) -> int:
        """Revoke all refresh tokens for a user."""
        tokens = self.db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked == False
        ).all()
        
        revoked_count = 0
        for token in tokens:
            token.is_revoked = True
            token.revoked_at = datetime.utcnow()
            revoked_count += 1
        
        self.db.commit()
        return revoked_count
    
    def cleanup_expired_tokens(self) -> int:
        """Remove expired refresh tokens from the database."""
        expired_tokens = self.db.query(RefreshToken).filter(
            RefreshToken.expires_at < datetime.utcnow()
        ).all()
        
        deleted_count = 0
        for token in expired_tokens:
            self.db.delete(token)
            deleted_count += 1
        
        self.db.commit()
        return deleted_count
