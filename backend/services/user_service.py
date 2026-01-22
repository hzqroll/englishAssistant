"""
User service.

Handles user CRUD operations and management.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from models import User, UserSettings, APICredit
from schemas.user import UserCreate, UserUpdate, UserResponse


class UserService:
    """
    User management service.

    Handles user creation, updates, and retrieval.

    Attributes:
        None
    """

    def create(self, data: UserCreate, db: Session) -> User:
        """
        Create a new user.

        Args:
            data: User creation data
            db: Database session

        Returns:
            Created User object

        Raises:
            UserServiceError: If creation fails
        """
        # TODO: Implement user creation
        # 1. Check if email exists
        # 2. Hash password
        # 3. Create user record
        # 4. Create user settings
        # 5. Return user

        existing = db.query(User).filter(User.email == data.email).first()
        if existing:
            raise UserServiceError("Email already exists")

        from core.security import hash_password

        user = User(
            email=data.email,
            password_hash=hash_password(data.password),
            tier=data.tier or "free",
            is_active=True,
            is_verified=False
        )
        db.add(user)

        settings = UserSettings(
            user_id=user.id,
            default_mode=data.default_mode or "accuracy"
        )
        db.add(settings)

        db.commit()
        db.refresh(user)

        return user

    def get(self, user_id: str, db: Session) -> Optional[User]:
        """
        Get user by ID.

        Args:
            user_id: User ID
            db: Database session

        Returns:
            User object or None
        """
        return db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str, db: Session) -> Optional[User]:
        """
        Get user by email.

        Args:
            email: User email
            db: Database session

        Returns:
            User object or None
        """
        return db.query(User).filter(User.email == email).first()

    def update(self, user: User, data: UserUpdate, db: Session) -> User:
        """
        Update user information.

        Args:
            user: User object
            data: Update data
            db: Database session

        Returns:
            Updated User object
        """
        # TODO: Implement user update
        if data.email is not None:
            user.email = data.email

        if data.tier is not None:
            user.tier = data.tier

        db.commit()
        db.refresh(user)

        return user

    def delete(self, user: User, db: Session) -> bool:
        """
        Delete user (soft delete).

        Args:
            user: User object
            db: Database session

        Returns:
            True if successful
        """
        # TODO: Implement soft delete
        from models.base import SoftDeleteMixin

        if isinstance(user, SoftDeleteMixin):
            user.soft_delete()
        else:
            db.delete(user)

        db.commit()
        return True

    def list_users(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """
        List all users with pagination.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum records to return

        Returns:
            List of User objects
        """
        return (
            db.query(User)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def to_response(self, user: User) -> UserResponse:
        """
        Convert User object to response schema.

        Args:
            user: User object

        Returns:
            UserResponse object
        """
        return UserResponse(
            id=str(user.id),
            email=user.email,
            tier=user.tier,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
            last_login_at=user.last_login_at
        )


class UserServiceError(Exception):
    """Exception raised for user service errors."""

    pass
