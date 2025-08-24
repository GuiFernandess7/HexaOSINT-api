import uuid
from typing import Optional, List
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, JSON, Boolean
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from .base_model import Base
from settings import settings
from datetime import datetime


class ScanHistory(Base):
    __tablename__ = settings.DB_SCAN_HISTORY
    __table_args__ = {"extend_existing": settings.DATABASE_SCHEMA}

    scan_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    search_type: Mapped[str] = mapped_column(nullable=False)
    engine: Mapped[str] = mapped_column(nullable=False)
    query: Mapped[Optional[str]] = mapped_column(nullable=True)
    image_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    id_search: Mapped[Optional[str]] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(nullable=False, default="STARTED")
    timestamp: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

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
