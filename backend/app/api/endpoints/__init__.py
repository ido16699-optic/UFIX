"""API endpoints package."""
from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.profiles import router as profiles_router
from app.api.endpoints.jobs import router as jobs_router
from app.api.endpoints.offers import router as offers_router
from app.api.endpoints.orders import router as orders_router
from app.api.endpoints.chat import router as chat_router
from app.api.endpoints.reviews import router as reviews_router
from app.api.endpoints.admin import router as admin_router

__all__ = [
    "auth_router",
    "profiles_router",
    "jobs_router",
    "offers_router",
    "orders_router",
    "chat_router",
    "reviews_router",
    "admin_router",
]
