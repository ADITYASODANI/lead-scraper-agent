"""
Agent 5: Pitch Generator Agent.
Synthesizes verified observations, prototype demo links, and tailored messaging into
three pitch formats (WhatsApp/DM, Email, and Detailed Proposal) with zero spammy guarantees.
"""

from datetime import datetime
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.agents.base import BaseAgent
from app.models import Lead, BusinessAnalysis, Prototype, Pitch
from app.services.llm_client import LLMClient
from app.config import get_settings

logger = logging.getLogger(__name__)


class PitchGeneratorAgent(BaseAgent):
    """Generates personalized sales pitches grounded in factual observations."""

    def __init__(self):
        super().__init__(name="pitch_generator_agent")
        self.llm_client = LLMClient()
        self.settings = get_settings()

    async def _run(
        self,
        db: AsyncSession,
        input_data: Dict[str, Any],
        lead_id: Optional[str] = None,
    ) -> tuple[Dict[str, Any], List[str]]:
        if not lead_id:
            raise ValueError("lead_id is required for PitchGeneratorAgent")

        lead = (await db.execute(select(Lead).where(Lead.id == lead_id))).scalar_one_or_none()
        if not lead:
            raise ValueError(f"Lead not found with id={lead_id}")

        lead.status = "GENERATING_PITCH"
        await db.commit()

        analysis = (await db.execute(
            select(BusinessAnalysis).where(BusinessAnalysis.lead_id == lead.id)
        )).scalar_one_or_none()

        proto = (await db.execute(
            select(Prototype).where(Prototype.lead_id == lead.id)
        )).scalar_one_or_none()

        demo_url = proto.preview_url if proto and proto.preview_url else f"{self.settings.dashboard_url}/preview/{lead.id}"
        sender_name = self.settings.sender_name
        observations = analysis.observations if analysis else ["Missing mobile-friendly web landing page"]

        system_prompt = (
            "You are a professional business development consultant. "
            "Write highly personalized, respectful pitches for this business based strictly on observed facts. "
            "CRITICAL RULES:\n"
            "- NEVER guarantee sales, rankings, or revenue.\n"
            "- NEVER claim fake problems or manipulate urgency.\n"
            "- Reference the actual observations and include the demo link.\n"
            "- Maintain an honest, friendly tone inviting collaborative customization.\n"
            "Output strict JSON format."
        )

        prompt = (
            f"Generate 3 customized pitches for:\n"
            f"Business: {lead.business_name}\n"
            f"Category: {lead.category}\n"
            f"Location: {lead.location}\n"
            f"Specific Observations: {observations}\n"
            f"Demo URL: {demo_url}\n"
            f"Sender Name: {sender_name}\n\n"
            f"Return JSON with keys:\n"
            f"- short_pitch (string suitable for WhatsApp/DM: concise, friendly, with demo link)\n"
            f"- email_pitch (string suitable for professional email: clear subject, respectful context, demo link)\n"
            f"- detailed_pitch (string suitable for formal introduction document)\n"
            f"- observations_referenced (list of strings mentioning the actual points addressed)"
        )

        context_hints = {
            "business_name": lead.business_name,
            "category": lead.category,
            "location": lead.location,
            "demo_url": demo_url,
            "observations": observations,
        }

        generated = await self.llm_client.generate_json(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.2,
            context_hints=context_hints,
        )

        short_p = generated.get("short_pitch") or (
            f"Hello {lead.business_name},\n\n"
            f"I was researching {lead.category.lower()} in {lead.location} and noticed you don't have an active mobile website. "
            f"I built a free interactive concept for {lead.business_name} to show how your online presence could look:\n\n"
            f"{demo_url}\n\n"
            f"This can be customized with your actual services and photos. Let me know if you'd like to discuss it!\n\n"
            f"Best,\n{sender_name}"
        )

        email_p = generated.get("email_pitch") or (
            f"Subject: Website Concept & Digital Presence for {lead.business_name}\n\n"
            f"Dear {lead.business_name} Team,\n\n"
            f"I came across your business while researching {lead.category.lower()} in {lead.location}. "
            f"I noticed that prospective clients searching on mobile currently don't find a dedicated website with your services and contact details.\n\n"
            f"To demonstrate the potential impact, I put together a working single-page prototype tailored for {lead.business_name}:\n"
            f"{demo_url}\n\n"
            f"The concept includes click-to-call, service highlights, and your location. It can be easily customized with your real information and brand colors.\n\n"
            f"Would you be open to a quick chat this week to explore this further?\n\n"
            f"Kind regards,\n{sender_name}"
        )

        detailed_p = generated.get("detailed_pitch") or (
            f"DIGITAL OPPORTUNITY PROPOSAL FOR {lead.business_name.upper()}\n\n"
            f"Location: {lead.location}\n"
            f"Prepared By: {sender_name}\n\n"
            f"1. CONTEXT & OBSERVATIONS\n"
            f"Consumers in {lead.location} routinely search for {lead.category.lower()} on smartphones. Currently, {lead.business_name} lacks an active web portal.\n\n"
            f"2. WORKING PROTOTYPE\n"
            f"Demo Link: {demo_url}\n\n"
            f"3. NEXT STEPS\n"
            f"Review the prototype. We can adapt it with your custom domain, imagery, and service details."
        )

        obs_ref = generated.get("observations_referenced", observations)

        # Persist pitch
        pitch_stmt = select(Pitch).where(Pitch.lead_id == lead.id)
        existing_pitch = (await db.execute(pitch_stmt)).scalar_one_or_none()

        if existing_pitch:
            existing_pitch.short_pitch = short_p
            existing_pitch.email_pitch = email_p
            existing_pitch.detailed_pitch = detailed_p
            existing_pitch.observations_referenced = obs_ref
            existing_pitch.demo_link = demo_url
            existing_pitch.generated_at = datetime.utcnow()
            pitch_record = existing_pitch
        else:
            pitch_record = Pitch(
                lead_id=lead.id,
                short_pitch=short_p,
                email_pitch=email_p,
                detailed_pitch=detailed_p,
                observations_referenced=obs_ref,
                demo_link=demo_url,
                generated_at=datetime.utcnow(),
            )
            db.add(pitch_record)

        # Transition lead status to HUMAN_REVIEW (PITCH_READY)
        lead.status = "HUMAN_REVIEW"
        lead.review_status = "PENDING"
        await db.commit()
        await db.refresh(pitch_record)

        output_payload = {
            "short_pitch": pitch_record.short_pitch,
            "email_pitch": pitch_record.email_pitch,
            "detailed_pitch": pitch_record.detailed_pitch,
            "observations_referenced": pitch_record.observations_referenced,
            "demo_link": pitch_record.demo_link,
        }

        logger.info("Pitch generated successfully for '%s'. Lead now in HUMAN_REVIEW.", lead.business_name)
        return output_payload, (analysis.source_urls if analysis else lead.source_urls)
