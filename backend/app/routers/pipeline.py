"""
Pipeline and Scheduler API Router.
Provides endpoints for manual runs, status checks,
and scheduler configuration.
"""

import asyncio
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db, AsyncSessionLocal
from app.schemas import PipelineRunRequest, PipelineRunResponse
from app.services.orchestrator import PipelineOrchestrator
from app.services.scheduler_service import SchedulerService

router = APIRouter(prefix="/pipeline", tags=["Pipeline & Scheduler"])

orchestrator = PipelineOrchestrator()
scheduler = SchedulerService.get_instance()


class ScheduleConfigRequest(BaseModel):
    interval_hours: int = Field(6, ge=5, le=10)
    enabled: bool = True


async def run_pipeline_task(
    category: str, location: str, max_leads: int
) -> None:
    """Async background task for pipeline runs."""
    async with AsyncSessionLocal() as session:
        await orchestrator.run_pipeline(
            db=session,
            category=category,
            location=location,
            max_leads=max_leads,
        )


@router.post("/run", response_model=PipelineRunResponse)
async def trigger_pipeline_run(
    request: PipelineRunRequest,
    background_tasks: BackgroundTasks,
    sync: bool = False,
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger immediate execution of the 5-agent pipeline.
    Supports synchronous execution or async background processing.
    """
    if orchestrator.is_running:
        raise HTTPException(
            status_code=409,
            detail="A pipeline execution is already in progress. Please wait for it to complete.",
        )

    if sync:
        result = await orchestrator.run_pipeline(
            db=db,
            category=request.category,
            location=request.location,
            max_leads=request.max_leads,
        )
        stats = result["stats"]
        return PipelineRunResponse(
            status="success",
            message=result["message"],
            leads_discovered=stats["leads_discovered"],
            leads_processed=stats["leads_processed"],
            qualified_count=stats["qualified_count"],
            rejected_count=stats["rejected_count"],
        )

    # Launch background task
    background_tasks.add_task(
        run_pipeline_task,
        request.category,
        request.location,
        request.max_leads,
    )

    return PipelineRunResponse(
        status="running",
        message=f"Pipeline started in background for '{request.category}' in '{request.location}'.",
        leads_discovered=0,
        leads_processed=0,
        qualified_count=0,
        rejected_count=0,
    )


@router.get("/status")
async def get_pipeline_status():
    """Check whether a pipeline run is actively executing."""
    return {"is_running": orchestrator.is_running}


@router.get("/scheduler")
async def get_scheduler_status():
    """Retrieve current scheduler configuration, interval, and next run timestamp."""
    return scheduler.get_status()


@router.post("/scheduler")
async def update_scheduler_config(config: ScheduleConfigRequest):
    """Update scheduler frequency (5, 6, 8, 10 hours) and enabled toggle."""
    try:
        updated = scheduler.update_schedule(
            interval_hours=config.interval_hours, enabled=config.enabled
        )
        return {"status": "success", "scheduler": updated}
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))
