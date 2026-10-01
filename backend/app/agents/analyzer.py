"""
Agent 2: Business Analysis Agent.
Analyzes business presence and digital footprint using deterministic HTTP probes
and contextual LLM synthesis.
"""

from datetime import datetime
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.agents.base import BaseAgent
from app.models import Lead, BusinessAnalysis
from app.services.scraper_service import ScraperService
from app.services.llm_client import LLMClient

logger = logging.getLogger(__name__)


class BusinessAnalysisAgent(BaseAgent):
    """Business Analysis Agent: evaluates online footprint and website status."""

    def __init__(self):
        super().__init__(name="business_analysis_agent")
        self.scraper_service = ScraperService()
        self.llm_client = LLMClient()

    async def _run(
        self,
        db: AsyncSession,
        input_data: Dict[str, Any],
        lead_id: Optional[str] = None,
    ) -> tuple[Dict[str, Any], List[str]]:
        if not lead_id:
            raise ValueError("lead_id is required for BusinessAnalysisAgent")

        stmt = select(Lead).where(Lead.id == lead_id)
        res = await db.execute(stmt)
        lead = res.scalar_one_or_none()
        if not lead:
            raise ValueError(f"Lead not found with id={lead_id}")

        lead.status = "ANALYZING"
        await db.commit()

        # Step 1: Deterministic Website Inspection (Zero LLM cost)
        probe_result = await self.scraper_service.probe_website(lead.website)
        website_status = probe_result["website_status"]
        probe_issues = probe_result.get("issues", [])

        # Step 2: Contextual Analysis via LLM
        system_prompt = (
            "You are an objective business systems analyst. "
            "Analyze the business and its digital presence based on observable evidence. "
            "Do not fabricate claims or criticize simply because a site is plain. "
            "Output strict JSON format."
        )

        prompt = (
            f"Analyze this business lead:\n"
            f"Business Name: {lead.business_name}\n"
            f"Category: {lead.category}\n"
            f"Location: {lead.location}\n"
            f"Phone: {lead.phone or 'Not listed'}\n"
            f"Existing Website URL: {lead.website or 'None'}\n"
            f"Technical Probe Status: {website_status}\n"
            f"Technical Probe Issues: {', '.join(probe_issues) if probe_issues else 'None'}\n\n"
            f"Return JSON with keys:\n"
            f"- businessName (string)\n"
            f"- websiteStatus (one of 'MISSING', 'PRESENT', 'NEEDS_IMPROVEMENT', 'UNKNOWN')\n"
            f"- businessSummary (string explaining what business does and customer base)\n"
            f"- currentDigitalPresence (string describing how it currently appears online)\n"
            f"- observations (list of observable strings)\n"
            f"- missingFeatures (list of strings representing digital capabilities it lacks)\n"
            f"- websiteOpportunity (boolean: true if a modern single-page website would meaningfully help)\n"
            f"- evidence (list of factual evidence strings)\n"
            f"- sourceUrls (list of URL strings)"
        )

        context_hints = {
            "business_name": lead.business_name,
            "category": lead.category,
            "location": lead.location,
            "phone": lead.phone,
            "website": lead.website,
            "source_urls": lead.source_urls,
        }

        llm_data = await self.llm_client.generate_json(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.2,
            context_hints=context_hints,
        )

        # Merge deterministic probe status if missing
        final_website_status = probe_result["website_status"]
        if final_website_status == "PRESENT" and llm_data.get("websiteStatus") == "NEEDS_IMPROVEMENT":
            final_website_status = "NEEDS_IMPROVEMENT"

        observations = llm_data.get("observations", [])
        if probe_issues:
            observations.extend(probe_issues)
        observations = list(dict.fromkeys(observations))  # remove dups

        evidence = llm_data.get("evidence", [])
        if not lead.website:
            evidence.append("No active website URL is registered on Google Maps listing")
        else:
            evidence.append(f"HTTP Probe detected: {website_status} (HTTPS: {probe_result.get('has_https')})")
        evidence = list(dict.fromkeys(evidence))

        source_urls = list(set(lead.source_urls + llm_data.get("sourceUrls", [])))

        # Upsert into business_analyses table
        analysis_stmt = select(BusinessAnalysis).where(BusinessAnalysis.lead_id == lead.id)
        existing_analysis = (await db.execute(analysis_stmt)).scalar_one_or_none()

        if existing_analysis:
            existing_analysis.website_status = final_website_status
            existing_analysis.business_summary = llm_data.get("businessSummary", f"{lead.business_name} in {lead.location}")
            existing_analysis.current_digital_presence = llm_data.get("currentDigitalPresence", "Limited online profile")
            existing_analysis.observations = observations
            existing_analysis.missing_features = llm_data.get("missingFeatures", [])
            existing_analysis.website_opportunity = bool(llm_data.get("websiteOpportunity", final_website_status != "PRESENT"))
            existing_analysis.evidence = evidence
            existing_analysis.source_urls = source_urls
            existing_analysis.analyzed_at = datetime.utcnow()
            analysis_record = existing_analysis
        else:
            analysis_record = BusinessAnalysis(
                lead_id=lead.id,
                website_status=final_website_status,
                business_summary=llm_data.get("businessSummary", f"{lead.business_name} in {lead.location}"),
                current_digital_presence=llm_data.get("currentDigitalPresence", "Limited online profile"),
                observations=observations,
                missing_features=llm_data.get("missingFeatures", []),
                website_opportunity=bool(llm_data.get("websiteOpportunity", final_website_status != "PRESENT")),
                evidence=evidence,
                source_urls=source_urls,
                analyzed_at=datetime.utcnow(),
            )
            db.add(analysis_record)

        lead.status = "ANALYZED"
        await db.commit()
        await db.refresh(analysis_record)

        output_payload = {
            "businessName": lead.business_name,
            "websiteStatus": analysis_record.website_status,
            "businessSummary": analysis_record.business_summary,
            "currentDigitalPresence": analysis_record.current_digital_presence,
            "observations": analysis_record.observations,
            "missingFeatures": analysis_record.missing_features,
            "websiteOpportunity": analysis_record.website_opportunity,
            "evidence": analysis_record.evidence,
            "sourceUrls": analysis_record.source_urls,
        }

        return output_payload, source_urls
