"""
Main FastAPI application entrypoint.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

from app.config import settings
from app.api import router
from app.background import start_background_poller


# Background task reference
background_task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for the FastAPI app.
    Starts background tasks on startup and cleans up on shutdown.
    """
    global background_task
    
    # Startup
    print("Starting application...")
    if settings.auto_fix:
        print("Auto-fix mode enabled. Starting background poller...")
        background_task = asyncio.create_task(start_background_poller())
    else:
        print("Auto-fix mode disabled. Fixes will be manual only.")
    
    yield
    
    # Shutdown
    print("Shutting down application...")
    if background_task:
        background_task.cancel()
        try:
            await background_task
        except asyncio.CancelledError:
            print("Background poller stopped.")


# Create FastAPI app
app = FastAPI(
    title="SonarQube Code Janitor API",
    description="AI-powered code fixer for SonarQube issues",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "SonarQube Code Janitor API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    from datetime import datetime
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
    }
