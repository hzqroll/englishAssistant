"""
Authentication service.

Handles JWT token generation, validation, and user authentication.
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from models import User
from core.security import create_access_token, verify_token, hash_password, verify_password
from schemas.auth import LoginRequest, RegisterRequest, AuthResponse


class AuthService:
    """
    Authentication service for user login, registration, and token management.

    Attributes:
        secret_key: JWT secret key
        algorithm: JWT algorithm
        access_token_expire_minutes: Access token expiration time
        refresh_token_expire_days: Refresh token expiration time
    """

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7
    ):
        """
        Initialize the authentication service.

        Args:
            secret_key: JWT secret key
            algorithm: JWT algorithm (default: HS256)
            access_token_expire_minutes: Access token expiration in minutes
            refresh_token_expire_days: Refresh token expiration in days
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days

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
            service = AuthService(secret_key="secret")
            request = RegisterRequest(email="user@example.com", password="pass123")
            response = service.register(request, db)
            assert response.access_token
            ```

        Raises:
            AuthServiceError: If registration fails
        """
        # TODO: Implement registration logic
        # 1. Check if email already exists
        # 2. Hash password
        # 3. Create user record
        # 4. Create user settings
        # 5. Generate tokens
        # 6. Return response

        # Check if user exists
        existing_user = db.query(User).filter(User.email == data.email).first()
        if existing_user:
            raise AuthServiceError("Email already registered")

        # Hash password
        password_hash = hash_password(data.password)

        # Create user
        user = User(
            email=data.email,
            password_hash=password_hash,
            tier="free",
            is_active=True,
            is_verified=False
        )
        db.add(user)
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
        # TODO: Implement login logic
        # 1. Find user by email
        # 2. Verify password
        # 3. Update last_login_at
        # 4. Generate tokens
        # 5. Return response

        # Find user
        user = db.query(User).filter(User.email == data.email).first()
        if not user:
            raise AuthServiceError("Invalid credentials")

        # Verify password
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
        # TODO: Implement token refresh logic
        # 1. Verify refresh token
        # 2. Check if user exists and is active
        # 3. Generate new access token
        # 4. Return response

        payload = verify_token(refresh_token, self.secret_key)
        if not payload or payload.get('type') != 'refresh':
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
        # TODO: Implement token verification
        return verify_token(token, self.secret_key)

    def _generate_tokens(self, user_id: str) -> Dict[str, str]:
        """
        Generate access and refresh tokens.

        Args:
            user_id: User ID

        Returns:
            Dictionary with access_token and refresh_token
        """
        # Access token
        access_expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user_id, "type": "access"},
            secret=self.secret_key,
            algorithm=self.algorithm,
            expires_delta=access_expire
        )

        # Refresh token
        refresh_expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        refresh_token = create_access_token(
            data={"sub": user_id, "type": "refresh"},
            secret=self.secret_key,
            algorithm=self.algorithm,
            expires_delta=refresh_expire
        )

        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }


class AuthServiceError(Exception):
    """Exception raised for authentication service errors."""

    pass
