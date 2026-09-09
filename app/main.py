"""
Main application entry point for ProgressPro API.
Configures FastAPI application, CORS middleware, exception handlers, and base health check routes.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict, Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.core.exceptions import ProgressProException, progresspro_exception_handler
from app.core.database import check_database_connection


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan context manager handles application startup and shutdown events.
    """
    # Startup actions
    setup_logging()
    logger.info("Starting up %s v%s", settings.APP_NAME, settings.APP_VERSION)
    logger.info("Environment: DEBUG=%s", settings.DEBUG)

    db_connected = check_database_connection()
    if db_connected:
        logger.info("Successfully connected to the database.")
    else:
        logger.warning(
            "Could not connect to the database at %s. Please verify MySQL server and .env settings.",
            settings.DB_HOST,
        )

    yield

    # Shutdown actions
    logger.info("Shutting down %s", settings.APP_NAME)


# Initialize FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "A software-only, data-driven REST API that analyzes historical fitness data "
        "and generates explainable training and basic nutrition recommendations using "
        "predefined sports-science rules."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from app.api.v1.router import api_v1_router

# Register custom exception handler
app.add_exception_handler(ProgressProException, progresspro_exception_handler)

# Mount API v1 Master Router
app.include_router(api_v1_router, prefix=settings.API_V1_STR)

# Mount Frontend UI Static Files
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.isdir(frontend_dir):
    app.mount("/ui", StaticFiles(directory=frontend_dir, html=True), name="ui")


@app.get("/dashboard", include_in_schema=False)
async def dashboard_redirect() -> RedirectResponse:
    """Convenience redirect to the frontend dashboard UI."""
    return RedirectResponse(url="/ui")


@app.get("/", tags=["Root"])
async def root() -> Dict[str, Any]:
    """
    Root welcome endpoint.
    Provides API identification and link to interactive documentation.
    """
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "docs_url": "/docs",
        "ui_url": "/ui",
    }


@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint.
    Verifies service liveness and reports database connectivity status.
    """
    db_status = "connected" if check_database_connection() else "disconnected"
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": db_status,
    }
