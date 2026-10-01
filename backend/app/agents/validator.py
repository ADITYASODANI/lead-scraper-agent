"""
Agent 3: Opportunity Validator Agent.
Critically qualifies business opportunities based on evidence, feasibility,
and calibrated confidence scoring.
"""

from datetime import datetime
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.agents.base import BaseAgent
from app.models import Lead, BusinessAnalysis, Opportunity
from app.services.llm_client import LLMClient

logger = logging.getLogger(__name__)


class OpportunityValidatorAgent(BaseAgent):
    """Opportunity Validator: decides if a lead warrants a prototype and pitch."""

    def __init__(self):
        super().__init__(name="opportunity_validator_agent")
        self.llm_client = LLMClient()

    async def _run(
        self,
        db: AsyncSession,
        input_data: Dict[str, Any],
        lead_id: Optional[str] = None,
    ) -> tuple[Dict[str, Any], List[str]]:
        if not lead_id:
            raise ValueError("lead_id is required for OpportunityValidatorAgent")

        # Load lead with analysis
        stmt = select(Lead).where(Lead.id == lead_id)
        res = await db.execute(stmt)
        lead = res.scalar_one_or_none()
        if not lead:
            raise ValueError(f"Lead not found with id={lead_id}")

        analysis_stmt = select(BusinessAnalysis).where(BusinessAnalysis.lead_id == lead.id)
        analysis = (await db.execute(analysis_stmt)).scalar_one_or_none()

        # Step 1: Pre-qualification heuristic check
        # If business has a completely working, HTTPS-enabled modern website without missing features, disqualify early
        if analysis and analysis.website_status == "PRESENT" and not analysis.website_opportunity:
            logger.info("Lead '%s' already has a comprehensive presence; early disqualifying.", lead.business_name)
            qualified = False
            priority = "LOW"
            confidence = 0.92
            reasoning = ["Business already operates an active, modern, functional website."]
            evidence = ["HTTP probe verified active website with no critical issues."]
            recommended_solution = "No website intervention needed at this stage."
            risks = ["High risk of cold outreach rejection due to existing web solution."]
        else:
            # Step 2: LLM Opportunity Evaluation
            system_prompt = (
                "You are an objective enterprise sales engineer and website opportunity validator. "
                "Evaluate whether creating a customized single-page website prototype is worth our time and relevant to the business. "
                "Do not blindly qualify every business. Require demonstrable evidence. "
                "Confidence must be between 0.0 and 1.0. Priority must be HIGH, MEDIUM, or LOW."
            )

            prompt = (
                f"Evaluate this business lead for website development qualification:\n"
                f"Business Name: {lead.business_name}\n"
                f"Category: {lead.category}\n"
                f"Location: {lead.location}\n"
                f"Phone: {lead.phone or 'Not listed'}\n"
                f"Website Status: {analysis.website_status if analysis else 'UNKNOWN'}\n"
                f"Observations: {analysis.observations if analysis else []}\n"
                f"Missing Features: {analysis.missing_features if analysis else []}\n\n"
                f"Decide if qualified for a prototype. Return JSON with:\n"
                f"- qualified (boolean)\n"
                f"- opportunityType (string, e.g. 'SINGLE_PAGE_WEBSITE')\n"
                f"- priority (one of 'HIGH', 'MEDIUM', 'LOW')\n"
                f"- confidence (float between 0.0 and 1.0)\n"
                f"- reasoning (list of strings explaining the decision)\n"
                f"- evidence (list of factual evidence points supporting decision)\n"
                f"- recommendedSolution (string summary of what site should feature)\n"
                f"- risks (list of possible friction points or objections)"
            )

            context_hints = {
                "business_name": lead.business_name,
                "category": lead.category,
                "location": lead.location,
                "website": lead.website,
            }

            llm_eval = await self.llm_client.generate_json(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.1,
                context_hints=context_hints,
            )

            qualified = bool(llm_eval.get("qualified", True))
            opportunity_type = llm_eval.get("opportunityType", "SINGLE_PAGE_WEBSITE")
            priority = llm_eval.get("priority", "MEDIUM").upper()
            if priority not in ("HIGH", "MEDIUM", "LOW"):
                priority = "MEDIUM"

            raw_confidence = llm_eval.get("confidence", 0.75)
            try:
                confidence = max(0.0, min(1.0, float(raw_confidence)))
            except (ValueError, TypeError):
                confidence = 0.7

            reasoning = llm_eval.get("reasoning", [])
            evidence = llm_eval.get("evidence", [])
            recommended_solution = llm_eval.get("recommendedSolution", "Modern single-page mobile landing page")
            risks = llm_eval.get("risks", [])

        # Persist Opportunity
        opp_stmt = select(Opportunity).where(Opportunity.lead_id == lead.id)
        existing_opp = (await db.execute(opp_stmt)).scalar_one_or_none()

        if existing_opp:
            existing_opp.qualified = qualified
            existing_opp.opportunity_type = opportunity_type if 'opportunity_type' in locals() else "SINGLE_PAGE_WEBSITE"
            existing_opp.priority = priority
            existing_opp.confidence = confidence
            existing_opp.reasoning = reasoning
            existing_opp.evidence = evidence
            existing_opp.recommended_solution = recommended_solution
            existing_opp.risks = risks
            existing_opp.validated_at = datetime.utcnow()
            opp_record = existing_opp
        else:
            opp_record = Opportunity(
                lead_id=lead.id,
                qualified=qualified,
                opportunity_type=opportunity_type if 'opportunity_type' in locals() else "SINGLE_PAGE_WEBSITE",
                priority=priority,
                confidence=confidence,
                reasoning=reasoning,
                evidence=evidence,
                recommended_solution=recommended_solution,
                risks=risks,
                validated_at=datetime.utcnow(),
            )
            db.add(opp_record)

        lead.status = "QUALIFIED" if qualified else "REJECTED"
        await db.commit()
        await db.refresh(opp_record)

        output_payload = {
            "qualified": opp_record.qualified,
            "opportunityType": opp_record.opportunity_type,
            "priority": opp_record.priority,
            "confidence": opp_record.confidence,
            "reasoning": opp_record.reasoning,
            "evidence": opp_record.evidence,
            "recommendedSolution": opp_record.recommended_solution,
            "risks": opp_record.risks,
        }

        return output_payload, (analysis.source_urls if analysis else lead.source_urls)
