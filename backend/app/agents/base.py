"""
Base Agent Module.
Provides abstract agent lifecycle, automatic execution logging, error isolation,
and standardized execution results.
"""

from abc import ABC, abstractmethod
from datetime import datetime
import logging
import time
from typing import Generic, TypeVar, Optional, List, Dict, Any
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import AgentRun

logger = logging.getLogger(__name__)

T = TypeVar("T")


class AgentResult(BaseModel, Generic[T]):
    """Standardized output contract for all agent operations."""
    status: str = Field(default="SUCCESS", description="SUCCESS, FAILED, or SKIPPED")
    agent_name: str
    lead_id: Optional[str] = None
    data: Optional[T] = None
    sources: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    duration_ms: float = 0.0
    completed_at: datetime = Field(default_factory=datetime.utcnow)


class BaseAgent(ABC):
    """
    Abstract base agent ensuring unified execution lifecycle,
    persistent audit logging to database, and reliable exception handling.
    """

    def __init__(self, name: str):
        self.name = name

    async def execute(
        self,
        db: AsyncSession,
        input_data: Dict[str, Any],
        lead_id: Optional[str] = None,
    ) -> AgentResult[Any]:
        """
        Executes the agent logic wrapped with performance timing, database run logging,
        and graceful error handling.
        """
        start_time = time.perf_counter()
        started_at = datetime.utcnow()

        # Create initial audit run record
        run_record = AgentRun(
            agent_name=self.name,
            lead_id=lead_id,
            started_at=started_at,
            status="RUNNING",
            input_data=input_data,
            output_data={},
            error_message=None,
        )
        db.add(run_record)
        await db.commit()
        await db.refresh(run_record)

        try:
            logger.info("Starting agent '%s' for lead_id=%s", self.name, lead_id)
            result_data, sources = await self._run(db=db, input_data=input_data, lead_id=lead_id)

            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            run_record.status = "SUCCESS"
            run_record.completed_at = datetime.utcnow()
            run_record.output_data = (
                result_data.model_dump() if hasattr(result_data, "model_dump")
                else (result_data if isinstance(result_data, dict) else {"result": str(result_data)})
            )
            await db.commit()

            return AgentResult(
                status="SUCCESS",
                agent_name=self.name,
                lead_id=lead_id,
                data=result_data,
                sources=sources,
                duration_ms=duration_ms,
            )

        except Exception as exc:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            error_msg = f"Agent '{self.name}' error: {str(exc)}"
            logger.exception("Agent '%s' failed for lead_id=%s: %s", self.name, lead_id, exc)

            run_record.status = "FAILED"
            run_record.completed_at = datetime.utcnow()
            run_record.error_message = error_msg
            await db.commit()

            return AgentResult(
                status="FAILED",
                agent_name=self.name,
                lead_id=lead_id,
                data=None,
                errors=[error_msg],
                duration_ms=duration_ms,
            )

    @abstractmethod
    async def _run(
        self,
        db: AsyncSession,
        input_data: Dict[str, Any],
        lead_id: Optional[str] = None,
    ) -> tuple[Any, List[str]]:
        """
        Core agent implementation to be implemented by concrete agent classes.
        Returns:
            Tuple of (output_data, list_of_source_urls)
        """
        raise NotImplementedError
