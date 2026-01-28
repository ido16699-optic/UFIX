"""Main FastAPI application."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.profiles import router as profiles_router
from app.api.endpoints.jobs import router as jobs_router
from app.api.endpoints.offers import router as offers_router
from app.api.endpoints.orders import router as orders_router
from app.api.endpoints.chat import router as chat_router
from app.api.endpoints.reviews import router as reviews_router
from app.api.endpoints.admin import router as admin_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    await init_db()
    yield
    # Shutdown
    pass


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="UFIX - Uber for Handymen MVP Platform",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(profiles_router, prefix="/api/v1")
app.include_router(jobs_router, prefix="/api/v1")
app.include_router(offers_router, prefix="/api/v1")
app.include_router(orders_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(reviews_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to UFIX API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
