"""
Background Scheduler Service using APScheduler.
Supports dynamic interval reconfiguration (5h, 6h, 8h, 10h, or manual/disabled),
and prevents overlapping runs.
"""

from datetime import datetime
import logging
from typing import Optional, Dict, Any
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.config import get_settings
from app.database import AsyncSessionLocal
from app.services.orchestrator import PipelineOrchestrator

logger = logging.getLogger(__name__)


class SchedulerService:
    """Manages periodic autonomous execution of the lead generation pipeline."""

    _instance: Optional["SchedulerService"] = None

    def __init__(self):
        self.settings = get_settings()
        self.scheduler = AsyncIOScheduler()
        self.orchestrator = PipelineOrchestrator()
        self.current_interval_hours = self.settings.schedule_interval_hours
        self.is_enabled = self.settings.scheduler_enabled
        self.last_run_time: Optional[datetime] = None
        self.last_run_status: Optional[str] = None
        self.job_id = "periodic_lead_pipeline"

    @classmethod
    def get_instance(cls) -> "SchedulerService":
        """Singleton accessor."""
        if cls._instance is None:
            cls._instance = SchedulerService()
        return cls._instance

    def start(self) -> None:
        """Start scheduler if enabled in settings."""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started.")

        if self.is_enabled:
            self._schedule_job(self.current_interval_hours)

    def shutdown(self) -> None:
        """Cleanly shutdown scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("Scheduler stopped.")

    def _schedule_job(self, hours: int) -> None:
        """Add or reschedule the periodic pipeline job."""
        if self.scheduler.get_job(self.job_id):
            self.scheduler.remove_job(self.job_id)

        self.scheduler.add_job(
            self._execute_scheduled_run,
            trigger=IntervalTrigger(hours=hours),
            id=self.job_id,
            name="Periodic Lead Discovery & Proposal Pipeline",
            replace_existing=True,
            coalesce=True,
            max_instances=1,
        )
        logger.info("Pipeline scheduled to run every %d hours.", hours)

    async def _execute_scheduled_run(self) -> None:
        """Execute scheduled pipeline job with its own DB session."""
        if self.orchestrator.is_running:
            logger.info("Skipping scheduled pipeline execution: previous run still in progress.")
            return

        logger.info("Triggering scheduled multi-agent pipeline run...")
        self.last_run_time = datetime.utcnow()
        try:
            async with AsyncSessionLocal() as session:
                await self.orchestrator.run_pipeline(
                    db=session,
                    category="Restaurants",
                    location="Downtown, CA",
                    max_leads=self.settings.max_scraped_per_run,
                )
            self.last_run_status = "SUCCESS"
            logger.info("Scheduled pipeline completed successfully.")
        except Exception as exc:
            self.last_run_status = f"FAILED: {str(exc)}"
            logger.exception("Scheduled pipeline encountered error: %s", exc)

    def update_schedule(self, interval_hours: int, enabled: bool = True) -> Dict[str, Any]:
        """Update scheduler configuration dynamically."""
        if interval_hours not in (5, 6, 8, 10):
            raise ValueError("Supported intervals are 5, 6, 8, or 10 hours.")

        self.current_interval_hours = interval_hours
        self.is_enabled = enabled

        if enabled:
            self._schedule_job(interval_hours)
        else:
            if self.scheduler.get_job(self.job_id):
                self.scheduler.remove_job(self.job_id)
            logger.info("Periodic pipeline scheduling disabled.")

        return self.get_status()

    def get_status(self) -> Dict[str, Any]:
        """Return current scheduler operational status and next run times."""
        job = self.scheduler.get_job(self.job_id) if self.scheduler.running else None
        next_run = job.next_run_time.isoformat() if job and job.next_run_time else None

        return {
            "enabled": self.is_enabled and (job is not None),
            "interval_hours": self.current_interval_hours,
            "next_run_at": next_run,
            "last_run_at": self.last_run_time.isoformat() if self.last_run_time else None,
            "last_run_status": self.last_run_status,
            "is_running_now": self.orchestrator.is_running,
        }
