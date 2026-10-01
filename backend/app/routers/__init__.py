"""Routers package initialization."""

from app.routers.leads import router as leads_router
from app.routers.pipeline import router as pipeline_router
from app.routers.stats import router as stats_router
from app.routers.websites import router as websites_router

__all__ = [
    "leads_router",
    "pipeline_router",
    "stats_router",
    "websites_router",
]
