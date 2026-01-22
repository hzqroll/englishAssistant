"""
API v1 routes package.

This package contains all API v1 routers.
"""

from fastapi import APIRouter
from . import auth, analysis, history, statistics, export, settings

# Create main API v1 router
router = APIRouter()

# Include all sub-routers
router.include_router(auth.router, prefix="/auth", tags=["authentication"])
router.include_router(analysis.router, tags=["analysis"])
router.include_router(history.router, prefix="/history", tags=["history"])
router.include_router(statistics.router, prefix="/statistics", tags=["statistics"])
router.include_router(export.router, prefix="/export", tags=["export"])
router.include_router(settings.router, prefix="/settings", tags=["settings"])

__all__ = ["router"]
