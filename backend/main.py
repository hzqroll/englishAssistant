"""
English Transfer Assistant - FastAPI Application Entry Point

This is the main application entry point for the English Transfer Assistant API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import settings
from middleware.auth_middleware import AuthMiddleware

# Create FastAPI application
app = FastAPI(
    title="English Transfer Assistant API",
    description="AI-powered English text correction and analysis tool",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Auth middleware
app.add_middleware(AuthMiddleware)



@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.

    Returns:
        JSONResponse with service health status
    """
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "english-assistant-api",
            "version": "0.1.0",
        },
    )


@app.get("/")
async def root():
    """
    Root endpoint - API information.

    Returns:
        JSONResponse with basic API information
    """
    return JSONResponse(
        status_code=200,
        content={
            "message": "English Transfer Assistant API",
            "version": "0.1.0",
            "docs": "/docs",
            "health": "/health",
        },
    )


# Include API routers
from api.v1 import auth, analysis, history, statistics, settings, llm_config

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(analysis.router, prefix="/api/v1", tags=["analysis"])
app.include_router(history.router, prefix="/api/v1", tags=["history"])
app.include_router(statistics.router, prefix="/api/v1/statistics", tags=["statistics"])
app.include_router(settings.router, prefix="/api/v1", tags=["settings"])
app.include_router(llm_config.router, tags=["LLM Configuration"])

# TODO: Uncomment when export router is implemented
# from api.v1 import export
# app.include_router(export.router, prefix="/api/v1/export", tags=["export"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
