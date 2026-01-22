"""
Authentication API routes.

Handles user registration, login, token refresh, and user info.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from models import get_db, User
from schemas.auth import RegisterRequest, LoginRequest, AuthResponse, RefreshTokenRequest
from services import AuthService

router = APIRouter()
security = HTTPBearer()

# TODO: Initialize auth service with config from settings
auth_service = AuthService(secret_key="YOUR_SECRET_KEY_HERE")


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user.

    Args:
        request: Registration request with email and password
        db: Database session

    Returns:
        AuthResponse with access and refresh tokens

    Raises:
        400: If email already exists or validation fails
    """
    # TODO: Implement registration endpoint
    # 1. Validate request data
    # 2. Call auth service to register user
    # 3. Return tokens

    try:
        response = auth_service.register(request, db)
        return response
    except AuthService.auth_service.AuthServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return tokens.

    Args:
        request: Login request with email and password
        db: Database session

    Returns:
        AuthResponse with access and refresh tokens

    Raises:
        401: If credentials are invalid
    """
    # TODO: Implement login endpoint
    try:
        response = auth_service.login(request, db)
        return response
    except AuthService.auth_service.AuthServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.

    Args:
        request: Refresh token request
        db: Database session

    Returns:
        AuthResponse with new access and refresh tokens

    Raises:
        401: If refresh token is invalid
    """
    # TODO: Implement token refresh endpoint
    try:
        response = auth_service.refresh_token(request.refresh_token, db)
        return response
    except AuthService.auth_service.AuthServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.get("/me")
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user information.

    Args:
        credentials: HTTP Bearer credentials
        db: Database session

    Returns:
        User information

    Raises:
        401: If token is invalid
    """
    # TODO: Implement get current user endpoint
    # 1. Verify access token
    # 2. Get user from database
    # 3. Return user info

    token = credentials.credentials
    payload = auth_service.verify_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    user_id = payload.get('sub')
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return {
        "id": str(user.id),
        "email": user.email,
        "tier": user.tier,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "created_at": user.created_at
    }
