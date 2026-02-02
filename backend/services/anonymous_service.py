"""
Anonymous user service.

Handles anonymous user management and conversion to registered users.
"""

from typing import Optional
from sqlalchemy.orm import Session
from fastapi import Request
import uuid

from models import User


class AnonymousUserService:
    """
    Anonymous user management service.

    Manages temporary anonymous users and conversion to registered users.

    Attributes:
        None
    """

    def __init__(self):
        """Initialize the anonymous user service."""

    async def create_or_get_anonymous(
        self,
        request: Request,
        db: Session
    ) -> User:
        """
        Create or get anonymous user based on session/fingerprint.

        Args:
            request: FastAPI request object
            db: Database session

        Returns:
            Anonymous User object

        Example:
            ```python
            service = AnonymousUserService()
            anon_user = await service.create_or_get_anonymous(request, db)
            ```
        """
        # TODO: Implement anonymous user management
        # 1. Check cookie for existing anon_user_id
        # 2. If found, verify user exists and is anonymous
        # 3. If not, create new anonymous user
        # 4. Return user

        anon_id = request.cookies.get("anon_user_id")

        if anon_id:
            user = db.query(User).filter(User.id == anon_id).first()
            if user and user.tier == "anonymous":
                return user

        # Create new anonymous user
        user = User(
            id=uuid.uuid4(),
            email=f"anon_{uuid.uuid4().hex}@temp.local",
            password_hash="",
            tier="anonymous",
            is_active=True,
            is_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    async def convert_to_registered(
        self,
        anon_user: User,
        email: str,
        password_hash: str,
        db: Session
    ) -> User:
        """
        Convert anonymous user to registered user.

        Args:
            anon_user: Anonymous user object
            email: Email address
            password_hash: Hashed password
            db: Database session

        Returns:
            Updated User object

        Raises:
            AnonymousUserServiceError: If conversion fails
        """
        # TODO: Implement user conversion
        # 1. Check if email already exists
        # 2. Update user record with email and password
        # 3. Change tier from anonymous to free
        # 4. Migrate any data (analyses, etc.)
        # 5. Return updated user

        existing = db.query(User).filter(User.email == email).first()
        if existing:
            raise AnonymousUserServiceError("Email already registered")

        anon_user.email = email
        anon_user.password_hash = password_hash
        anon_user.tier = "free"
        anon_user.is_verified = False

        db.commit()
        db.refresh(anon_user)

        return anon_user

    async def migrate_anonymous_data(
        self,
        from_user: User,
        to_user: User,
        db: Session
    ) -> None:
        """
        Migrate data from anonymous to registered user.

        Args:
            from_user: Anonymous user
            to_user: Registered user
            db: Database session
        """
        # TODO: Implement data migration
        # 1. Reassign analyses to new user
        # 2. Reassign tags to new user
        # 3. Update audit trail
        # 4. Optionally delete old anonymous user

        from models import Analysis, Tag

        # Migrate analyses
        analyses = db.query(Analysis).filter(Analysis.user_id == from_user.id).all()
        for analysis in analyses:
            analysis.user_id = to_user.id

        # Migrate tags
        tags = db.query(Tag).filter(Tag.user_id == from_user.id).all()
        for tag in tags:
            tag.user_id = to_user.id

        db.commit()

    def is_anonymous(self, user: User) -> bool:
        """
        Check if user is anonymous.

        Args:
            user: User object

        Returns:
            True if anonymous, False otherwise
        """
        return user.tier == "anonymous"

    def generate_anonymous_email(self) -> str:
        """
        Generate unique anonymous email.

        Returns:
            Anonymous email address
        """
        return f"anon_{uuid.uuid4().hex}@temp.local"


class AnonymousUserServiceError(Exception):
    """Exception raised for anonymous user service errors."""

    pass
