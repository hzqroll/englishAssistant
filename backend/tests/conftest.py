"""
Pytest configuration and fixtures.

Provides common fixtures for testing.
"""

import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from models import Base, get_db
from models.user import User, UserSettings
from core.security import hash_password


# Test database URL (use in-memory SQLite for tests)
TEST_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture(scope="function")
def test_engine():
    """
    Create test database engine.

    Returns:
        Engine instance
    """
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_db(test_engine) -> Generator[Session, None, None]:
    """
    Create test database session.

    Args:
        test_engine: Test engine fixture

    Yields:
        Database session
    """
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def test_user(test_db: Session) -> User:
    """
    Create test user.

    Args:
        test_db: Test database session

    Returns:
        User object
    """
    user = User(
        email="test@example.com",
        password_hash=hash_password("test_password"),
        tier="free",
        is_active=True,
        is_verified=True
    )
    test_db.add(user)

    settings = UserSettings(
        user_id=user.id,
        default_mode="accuracy"
    )
    test_db.add(settings)
    test_db.commit()

    return user


@pytest.fixture(scope="function")
def test_client():
    """
    Create test FastAPI client.

    Returns:
        TestClient instance
    """
    # TODO: Implement test client fixture
    # from fastapi.testclient import TestClient
    # from main import app
    # return TestClient(app)
    pass


@pytest.fixture(scope="function")
def auth_headers(test_user: User) -> dict:
    """
    Create authentication headers for test user.

    Args:
        test_user: Test user fixture

    Returns:
        Dictionary with Authorization header
    """
    # TODO: Implement auth headers fixture
    # from core.security import create_access_token
    # token = create_access_token(
    #     data={"sub": str(test_user.id), "type": "access"},
    #     secret="test_secret"
    # )
    # return {"Authorization": f"Bearer {token}"}
    pass
