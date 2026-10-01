"""
Main FastAPI Application Entrypoint.
Orchestrates lifespan startup, CORS configuration, database initialization,
and REST routing for the Multi-Agent Lead Generation System.
"""

from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database import init_db
from app.routers import (
    leads_router,
    pipeline_router,
    stats_router,
    websites_router,
)
from app.services.scheduler_service import SchedulerService

# Configure logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("multi_agent_lead_gen")

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management."""
    logger.info("Initializing database tables...")
    await init_db()

    logger.info("Starting background scheduler...")
    scheduler = SchedulerService.get_instance()
    scheduler.start()

    yield

    logger.info("Shutting down background scheduler...")
    scheduler.shutdown()
    logger.info("Application shutdown complete.")


app = FastAPI(
    title="Multi-Agent Business Lead Discovery & Website Proposal System",
    description="Autonomous multi-agent pipeline discovering leads, qualifying opportunities, generating website prototypes, and preparing personalized pitches for human review.",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for the dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        settings.dashboard_url,
        *[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    ],
    allow_origin_regex=settings.cors_origin_regex or None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(leads_router, prefix=settings.api_prefix)
app.include_router(pipeline_router, prefix=settings.api_prefix)
app.include_router(stats_router, prefix=settings.api_prefix)
app.include_router(websites_router, prefix=settings.api_prefix)


@app.get("/api/health", tags=["Health"])
async def health_check():
    """System health check endpoint."""
    return {
        "status": "healthy",
        "service": "multi-agent-lead-generation-system",
        "version": "1.0.0",
        "llm_provider": settings.llm_provider,
        "scheduler_enabled": settings.scheduler_enabled,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
