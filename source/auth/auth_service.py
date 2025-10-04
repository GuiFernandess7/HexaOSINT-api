import uuid
from datetime import datetime, timedelta
from typing import Optional
import jwt
import bcrypt
from sqlalchemy.orm import Session
from database.models.db_models import User
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
            (User.username == user_data.username) | (User.email == user_data.email)
        ).first()
        
        if existing_user:
            if existing_user.username == user_data.username or existing_user.email == user_data.email:
                raise ValueError("User already exists.")
        
        # Create new user
        hashed_password = self.hash_password(user_data.password)
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            is_active=True,
            is_admin=False
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username and password."""
        user = self.db.query(User).filter(User.username == username).first()
        
        if not user:
            return None
        
        if not self.verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            return None
        
        # Update last login
        user.last_login = datetime.utcnow()
        self.db.commit()
        
        return user
    
    def create_access_token(self, user: User, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=24)  # Default 24 hours
        
        to_encode = {
            "sub": str(user.user_id),
            "username": user.username,
            "is_admin": user.is_admin,
            "exp": expire
        }
        
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_AUTH_KEY, algorithm="HS256")
        return encoded_jwt
    
    def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Get a user by their ID."""
        return self.db.query(User).filter(User.user_id == user_id).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by their username."""
        return self.db.query(User).filter(User.username == username).first()
    
    def update_user_last_login(self, user_id: uuid.UUID):
        """Update the last login timestamp for a user."""
        user = self.get_user_by_id(user_id)
        if user:
            user.last_login = datetime.utcnow()
            self.db.commit()
