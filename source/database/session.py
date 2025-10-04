from contextlib import contextmanager
from .base import SessionLocal


@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def get_db():
    """FastAPI dependency to get database session."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()