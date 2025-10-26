import uuid
from typing import Optional, List
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, JSON, Boolean, DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from .base_model import Base
from settings import settings
from datetime import datetime, timedelta


class User(Base):
    __tablename__ = settings.DB_USER
    __table_args__ = {"extend_existing": settings.DATABASE_SCHEMA}

    user_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    first_name: Mapped[str] = mapped_column(String(25), nullable=False)
    last_name: Mapped[str] = mapped_column(String(25), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    scans: Mapped[List["ScanHistory"]] = relationship(
        "ScanHistory", back_populates="user", cascade="all, delete-orphan"
    )
    
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )


class RefreshToken(Base):
    __tablename__ = settings.DB_REFRESH_TOKEN
    __table_args__ = {"extend_existing": settings.DATABASE_SCHEMA}

    token_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(f"{settings.DB_USER}.user_id"), nullable=False
    )
    token: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    device_info: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")


class ScanHistory(Base):
    __tablename__ = settings.DB_SCAN_HISTORY
    __table_args__ = {"extend_existing": settings.DATABASE_SCHEMA}

    scan_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(f"{settings.DB_USER}.user_id"), nullable=False
    )
    search_type: Mapped[str] = mapped_column(nullable=False)
    engine: Mapped[str] = mapped_column(nullable=False)
    query: Mapped[Optional[str]] = mapped_column(nullable=True)
    image_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    id_search: Mapped[Optional[str]] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(nullable=False, default="STARTED")
    timestamp: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="scans")
    results: Mapped[List["TargetResult"]] = relationship(
        "TargetResult", back_populates="scan", cascade="all, delete-orphan"
    )


class TargetResult(Base):
    __tablename__ = settings.DB_TARGET_RESULT
    __table_args__ = {"extend_existing": settings.DATABASE_SCHEMA}

    result_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    scan_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("scan_history.scan_id"), nullable=False
    )
    title: Mapped[Optional[str]] = mapped_column(nullable=True)
    link: Mapped[Optional[str]] = mapped_column(nullable=True)
    snippet: Mapped[Optional[str]] = mapped_column(nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(nullable=True)
    source_type: Mapped[Optional[str]] = mapped_column(nullable=True)
    score: Mapped[Optional[float]] = mapped_column(nullable=True)
    processed: Mapped[bool] = mapped_column(default=False, nullable=False)

    scan: Mapped["ScanHistory"] = relationship("ScanHistory", back_populates="results")
