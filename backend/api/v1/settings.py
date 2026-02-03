"""
Settings API routes.

Handles user settings management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

from models import get_db, User, UserSettings
from core.security import get_current_user

router = APIRouter()


class SettingsUpdate(BaseModel):
    """Request model for settings update."""
    default_mode: Optional[str] = Field(None, description="Default correction mode")
    theme: Optional[str] = Field(None, description="UI theme")
    auto_save: Optional[bool] = Field(None, description="Auto-save preference")
    preferences: Optional[Dict[str, Any]] = Field(None, description="Additional preferences")


class SettingsResponse(BaseModel):
    """Response model for settings."""
    user_id: str
    default_mode: str
    theme: str
    auto_save: bool
    preferences: Dict[str, Any]


@router.get("/settings", response_model=SettingsResponse)
async def get_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> SettingsResponse:
    """
    Get user's current settings.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        User settings

    Raises:
        401: If authentication fails
    """
    try:
        # Get or create user settings
        settings = db.query(UserSettings).filter(
            UserSettings.user_id == current_user.id
        ).first()

        if not settings:
            # Create default settings if they don't exist
            settings = UserSettings(
                user_id=current_user.id,
                default_mode="accuracy",
                theme="light",
                auto_save=True,
                preferences={}
            )
            db.add(settings)
            db.commit()
            db.refresh(settings)

        return SettingsResponse(
            user_id=str(settings.user_id),
            default_mode=settings.default_mode,
            theme=settings.theme,
            auto_save=settings.auto_save,
            preferences=settings.preferences or {}
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve settings: {str(e)}"
        )


@router.put("/settings", response_model=SettingsResponse)
async def update_settings(
    request: SettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> SettingsResponse:
    """
    Update user's settings.

    Args:
        request: Settings update request
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated settings

    Raises:
        400: If validation fails
        401: If authentication fails
    """
    try:
        # Get or create settings
        settings = db.query(UserSettings).filter(
            UserSettings.user_id == current_user.id
        ).first()

        if not settings:
            settings = UserSettings(
                user_id=current_user.id,
                default_mode="accuracy",
                theme="light",
                auto_save=True,
                preferences={}
            )
            db.add(settings)

        # Update fields if provided
        if request.default_mode is not None:
            # Validate mode
            if request.default_mode not in ['accuracy', 'natural']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid mode. Must be 'accuracy' or 'natural'"
                )
            settings.default_mode = request.default_mode

        if request.theme is not None:
            # Validate theme
            if request.theme not in ['light', 'dark', 'auto']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid theme. Must be 'light', 'dark', or 'auto'"
                )
            settings.theme = request.theme

        if request.auto_save is not None:
            settings.auto_save = request.auto_save

        if request.preferences is not None:
            # Merge preferences
            current_prefs = settings.preferences or {}
            current_prefs.update(request.preferences)
            settings.preferences = current_prefs

        db.commit()
        db.refresh(settings)

        return SettingsResponse(
            user_id=str(settings.user_id),
            default_mode=settings.default_mode,
            theme=settings.theme,
            auto_save=settings.auto_save,
            preferences=settings.preferences or {}
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update settings: {str(e)}"
        )
