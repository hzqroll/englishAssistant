"""
Authentication API routes.

Handles user registration, login, token refresh, and user info.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from models import get_db, User
from schemas.auth import RegisterRequest, LoginRequest, AuthResponse, RefreshTokenRequest, UserResponse
from services.auth_service import AuthService, AuthServiceError
from core.security import get_current_user

router = APIRouter()
auth_service = AuthService()


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
    try:
        response = auth_service.register(request, db)
        return response
    except AuthServiceError as e:
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
    try:
        response = auth_service.login(request, db)
        return response
    except AuthServiceError as e:
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
    try:
        response = auth_service.refresh_token(request.refresh_token, db)
        return response
    except AuthServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information.

    Args:
        current_user: Current authenticated user (injected by dependency)

    Returns:
        User information

    Raises:
        401: If token is invalid or user not found
    """
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        tier=current_user.tier,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
        last_login_at=current_user.last_login_at
    )
