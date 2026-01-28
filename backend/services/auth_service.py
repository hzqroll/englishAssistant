"""
Authentication service.

Handles JWT token generation, validation, and user authentication.
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from models import User
from models.user import UserSettings
from core.security import create_access_token, create_refresh_token, verify_token
from core.config import settings
from schemas.auth import LoginRequest, RegisterRequest, AuthResponse


class AuthService:
    """
    Authentication service for user login, registration, and token management.

    Uses settings from core.config for JWT configuration.
    """

    def __init__(self):
        """
        Initialize the authentication service.

        Uses settings from core.config:
        - JWT_SECRET_KEY
        - JWT_ALGORITHM
        - ACCESS_TOKEN_EXPIRE_MINUTES
        - REFRESH_TOKEN_EXPIRE_DAYS
        """
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.REFRESH_TOKEN_EXPIRE_DAYS

    def register(self, data: RegisterRequest, db: Session) -> AuthResponse:
        """
        Register a new user.

        Args:
            data: Registration request data
            db: Database session

        Returns:
            AuthResponse with access and refresh tokens

        Example:
            ```python
            service = AuthService()
            request = RegisterRequest(email="user@example.com", password="pass123")
            response = service.register(request, db)
            assert response.access_token
            ```

        Raises:
            AuthServiceError: If registration fails
        """
        # Check if user exists
        existing_user = db.query(User).filter(User.email == data.email).first()
        if existing_user:
            raise AuthServiceError("Email already registered")

        # Hash password using security module
        from core.security import hash_password
        password_hash = hash_password(data.password)

        # Create user
        user = User(
            email=data.email,
            password_hash=password_hash,
            tier=data.tier or "free",
            is_active=True,
            is_verified=False
        )
        db.add(user)
        db.flush()  # Flush to get user.id

        # Create user settings
        user_settings = UserSettings(
            user_id=user.id,
            default_mode=data.default_mode or "accuracy"
        )
        db.add(user_settings)

        db.commit()
        db.refresh(user)

        # Generate tokens
        tokens = self._generate_tokens(str(user.id))

        return AuthResponse(
            access_token=tokens['access_token'],
            refresh_token=tokens['refresh_token'],
            token_type="bearer",
            expires_in=self.access_token_expire_minutes * 60,
            user_id=str(user.id),
            email=user.email,
            tier=user.tier
        )

    def login(self, data: LoginRequest, db: Session) -> AuthResponse:
        """
        Authenticate user and generate tokens.

        Args:
            data: Login request data
            db: Database session

        Returns:
            AuthResponse with tokens

        Raises:
            AuthServiceError: If authentication fails
        """
        # Find user
        user = db.query(User).filter(User.email == data.email).first()
        if not user:
            raise AuthServiceError("Invalid credentials")

        # Verify password
        from core.security import verify_password
        if not verify_password(data.password, user.password_hash):
            raise AuthServiceError("Invalid credentials")

        # Check if active
        if not user.is_active:
            raise AuthServiceError("Account is disabled")

        # Update last login
        user.last_login_at = datetime.utcnow()
        db.commit()

        # Generate tokens
        tokens = self._generate_tokens(str(user.id))

        return AuthResponse(
            access_token=tokens['access_token'],
            refresh_token=tokens['refresh_token'],
            token_type="bearer",
            expires_in=self.access_token_expire_minutes * 60,
            user_id=str(user.id),
            email=user.email,
            tier=user.tier
        )

    def refresh_token(self, refresh_token: str, db: Session) -> AuthResponse:
        """
        Refresh access token using refresh token.

        Args:
            refresh_token: Refresh token
            db: Database session

        Returns:
            AuthResponse with new access token

        Raises:
            AuthServiceError: If refresh fails
        """
        payload = verify_token(refresh_token)
        if not payload:
            raise AuthServiceError("Invalid refresh token")

        user_id = payload.get('sub')
        user = db.query(User).filter(User.id == user_id).first()

        if not user or not user.is_active:
            raise AuthServiceError("User not found or inactive")

        # Generate new tokens
        tokens = self._generate_tokens(str(user.id))

        return AuthResponse(
            access_token=tokens['access_token'],
            refresh_token=tokens['refresh_token'],
            token_type="bearer",
            expires_in=self.access_token_expire_minutes * 60,
            user_id=str(user.id),
            email=user.email,
            tier=user.tier
        )

    def verify_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify access token and return payload.

        Args:
            token: Access token

        Returns:
            Token payload if valid, None otherwise

        Example:
            ```python
            payload = service.verify_access_token(token)
            if payload:
                user_id = payload.get('sub')
            ```
        """
        return verify_token(token)

    def _generate_tokens(self, user_id: str) -> Dict[str, str]:
        """
        Generate access and refresh tokens.

        Args:
            user_id: User ID

        Returns:
            Dictionary with access_token and refresh_token
        """
        # Access token
        access_token = create_access_token(
            data={"sub": user_id, "type": "access"},
            expires_delta=timedelta(minutes=self.access_token_expire_minutes)
        )

        # Refresh token
        refresh_token = create_refresh_token(
            data={"sub": user_id, "type": "refresh"}
        )

        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }


class AuthServiceError(Exception):
    """Exception raised for authentication service errors."""

    pass
