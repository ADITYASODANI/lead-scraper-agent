"""
Pipeline Orchestrator Service.
Coordinates the end-to-end multi-agent workflow:
Discovery -> Analysis -> Qualification -> Website Prototype -> Pitch -> Human Review.
Ensures fault isolation, and concurrency guards.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.agents.discovery import LeadDiscoveryAgent
from app.agents.analyzer import BusinessAnalysisAgent
from app.agents.validator import OpportunityValidatorAgent
from app.agents.generator import WebsiteGeneratorAgent
from app.agents.pitch import PitchGeneratorAgent
from app.models import Lead

logger = logging.getLogger(__name__)


class PipelineOrchestrator:
    """Orchestrates multi-agent execution pipeline across leads."""

    _is_running: bool = False

    def __init__(self):
        self.discovery_agent = LeadDiscoveryAgent()
        self.analysis_agent = BusinessAnalysisAgent()
        self.validator_agent = OpportunityValidatorAgent()
        self.generator_agent = WebsiteGeneratorAgent()
        self.pitch_agent = PitchGeneratorAgent()

    @property
    def is_running(self) -> bool:
        """Check if pipeline execution is currently active."""
        return PipelineOrchestrator._is_running

    async def run_pipeline(
        self,
        db: AsyncSession,
        category: str = "Restaurants",
        location: str = "Downtown, CA",
        max_leads: int = 5,
    ) -> Dict[str, Any]:
        """
        Execute full multi-agent pipeline for a target category and location.
        """
        if PipelineOrchestrator._is_running:
            raise RuntimeError("Pipeline run already in progress. Please wait for completion.")

        PipelineOrchestrator._is_running = True
        logger.info("Pipeline started for category='%s', location='%s' (max=%d)", category, location, max_leads)

        stats = {
            "leads_discovered": 0,
            "leads_processed": 0,
            "qualified_count": 0,
            "rejected_count": 0,
            "failed_count": 0,
            "details": [],
        }

        try:
            # Stage 1: Lead Discovery & Deduplication
            discovery_result = await self.discovery_agent.execute(
                db=db,
                input_data={
                    "category": category,
                    "location": location,
                    "max_leads": max_leads,
                },
            )

            discovered_leads: List[Dict[str, Any]] = discovery_result.data or []
            stats["leads_discovered"] = len(discovered_leads)

            # Stage 2: Process each lead through the sequential agent pipeline
            for lead_info in discovered_leads:
                lead_id = lead_info["lead_id"]
                biz_name = lead_info["business_name"]
                logger.info("Processing pipeline for lead: '%s' (id=%s)", biz_name, lead_id)
                stats["leads_processed"] += 1

                try:
                    lead_summary = await self.process_single_lead(db=db, lead_id=lead_id)
                    if lead_summary.get("qualified"):
                        stats["qualified_count"] += 1
                    else:
                        stats["rejected_count"] += 1
                    stats["details"].append(lead_summary)

                except Exception as lead_err:
                    logger.exception("Failed processing lead '%s' (id=%s): %s", biz_name, lead_id, lead_err)
                    stats["failed_count"] += 1
                    # Mark lead as FAILED in database
                    failed_lead = (await db.execute(select(Lead).where(Lead.id == lead_id))).scalar_one_or_none()
                    if failed_lead:
                        failed_lead.status = "FAILED"
                        await db.commit()
                    stats["details"].append({
                        "lead_id": lead_id,
                        "business_name": biz_name,
                        "status": "FAILED",
                        "error": str(lead_err),
                    })

            return {
                "status": "success",
                "message": f"Pipeline completed. Processed {stats['leads_processed']} leads.",
                "stats": stats,
            }

        finally:
            PipelineOrchestrator._is_running = False

    async def process_single_lead(self, db: AsyncSession, lead_id: str) -> Dict[str, Any]:
        """
        Run the sequential pipeline for an individual lead:
        Analysis -> Qualification -> (if qualified: Prototype -> Pitch).
        """
        lead = (await db.execute(select(Lead).where(Lead.id == lead_id))).scalar_one_or_none()
        if not lead:
            raise ValueError(f"Lead not found with id={lead_id}")

        # 1. Business Analysis Agent
        analysis_res = await self.analysis_agent.execute(
            db=db, input_data={}, lead_id=lead_id
        )
        if analysis_res.status != "SUCCESS":
            raise RuntimeError(f"Business Analysis failed: {analysis_res.errors}")

        # 2. Opportunity Validator Agent
        validator_res = await self.validator_agent.execute(
            db=db, input_data={}, lead_id=lead_id
        )
        if validator_res.status != "SUCCESS":
            raise RuntimeError(f"Opportunity Validator failed: {validator_res.errors}")

        is_qualified = bool(validator_res.data and validator_res.data.get("qualified"))

        if not is_qualified:
            logger.info("Lead '%s' was rejected by Opportunity Validator.", lead.business_name)
            return {
                "lead_id": lead_id,
                "business_name": lead.business_name,
                "qualified": False,
                "status": "REJECTED",
                "reasoning": validator_res.data.get("reasoning", []) if validator_res.data else [],
            }

        # 3. Single-Page Website Generator Agent
        generator_res = await self.generator_agent.execute(
            db=db, input_data={}, lead_id=lead_id
        )
        if generator_res.status != "SUCCESS":
            raise RuntimeError(f"Website Generator failed: {generator_res.errors}")

        # 4. Pitch Generator Agent
        pitch_res = await self.pitch_agent.execute(
            db=db, input_data={}, lead_id=lead_id
        )
        if pitch_res.status != "SUCCESS":
            raise RuntimeError(f"Pitch Generator failed: {pitch_res.errors}")

        return {
            "lead_id": lead_id,
            "business_name": lead.business_name,
            "qualified": True,
            "status": "HUMAN_REVIEW",
            "prototype_ready": True,
            "pitch_ready": True,
        }
