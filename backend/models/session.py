"""
Database session management.

This module provides database connection and session management utilities.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from core.config import settings


# Create database engine
# TODO: Configure engine based on settings (PostgreSQL connection)
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.DEBUG
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.

    This is typically used with FastAPI's dependency injection:

    ```python
    @app.get("/users")
    def get_users(db: Session = Depends(get_db)):
        return db.query(User).all()
    ```

    Yields:
        Session: SQLAlchemy database session

    Example:
        ```python
        with next(get_db()) as db:
            users = db.query(User).all()
        ```
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database tables.

    Creates all tables defined in models. Use this for development/testing.
    For production, use Alembic migrations instead.
    """
    from .base import Base
    Base.metadata.create_all(bind=engine)


def drop_db() -> None:
    """
    Drop all database tables.

    WARNING: This will delete all data. Use only for testing.
    """
    from .base import Base
    Base.metadata.drop_all(bind=engine)
