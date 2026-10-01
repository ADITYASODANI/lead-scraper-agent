"""
Agent 4: Single-Page Website Generator.
Generates modern, responsive, component-structured single-page website prototypes
grounded strictly in factual business data without fabricated awards or claims.
"""

from datetime import datetime
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.agents.base import BaseAgent
from app.models import Lead, BusinessAnalysis, Opportunity, Prototype
from app.services.llm_client import LLMClient
from app.config import get_settings
from app.services.design_themes import pick_design

logger = logging.getLogger(__name__)


class WebsiteGeneratorAgent(BaseAgent):
    """Generates structured single-page website prototypes for qualified leads."""

    def __init__(self):
        super().__init__(name="website_generator_agent")
        self.llm_client = LLMClient()
        self.settings = get_settings()

    async def _run(
        self,
        db: AsyncSession,
        input_data: Dict[str, Any],
        lead_id: Optional[str] = None,
    ) -> tuple[Dict[str, Any], List[str]]:
        if not lead_id:
            raise ValueError("lead_id is required for WebsiteGeneratorAgent")

        stmt = select(Lead).where(Lead.id == lead_id)
        lead = (await db.execute(stmt)).scalar_one_or_none()
        if not lead:
            raise ValueError(f"Lead not found with id={lead_id}")

        lead.status = "GENERATING_WEBSITE"
        await db.commit()

        analysis_stmt = select(BusinessAnalysis).where(BusinessAnalysis.lead_id == lead.id)
        analysis = (await db.execute(analysis_stmt)).scalar_one_or_none()

        opp_stmt = select(Opportunity).where(Opportunity.lead_id == lead.id)
        opp = (await db.execute(opp_stmt)).scalar_one_or_none()

        # Unique per-lead visual design (palette, fonts, layout). Keep a lead's
        # rotation slot on regeneration; new leads take the next slot.
        existing_cfg = (await db.execute(
            select(Prototype.full_config).where(Prototype.lead_id == lead.id)
        )).scalar_one_or_none() or {}
        design_index = (existing_cfg.get("design") or {}).get("index")
        if design_index is None:
            design_index = (await db.execute(select(func.count(Prototype.id)))).scalar_one()
        design = pick_design(lead.id, lead.category, index=design_index)
        palette = design["palette"]

        # Generate custom structured copy via LLM
        system_prompt = (
            "You are an elite web designer and conversion copywriter. "
            "Generate a complete, modern single-page website prototype structure for this local business. "
            "CRITICAL SAFETY RULE: Do NOT invent fake customer review counts, fake awards, fake years of experience, or fake certifications. "
            "Use only verified business facts and standard professional services suited to their category. "
            "Make the copy specific to this exact business type and name, never generic: e.g. a cafe or restaurant "
            "lists signature dishes/drinks as its services (a menu), a salon lists treatments, a gym lists programs. "
            "Vary tone and wording so no two businesses read alike. "
            "Output strict JSON format."
        )

        prompt = (
            f"Generate a customized website prototype for this verified business:\n"
            f"Business Name: {lead.business_name}\n"
            f"Category: {lead.category}\n"
            f"Location: {lead.location}\n"
            f"Phone: {lead.phone or 'Contact for inquiries'}\n"
            f"Email: {lead.email or ''}\n"
            f"Digital Opportunity Focus: {opp.recommended_solution if opp else 'Modern single-page presence'}\n\n"
            f"Return a JSON object containing:\n"
            f"- site_title (string)\n"
            f"- tagline (string)\n"
            f"- hero_section: {{\"headline\": str, \"subheadline\": str, \"primary_cta\": str, \"secondary_cta\": str}}\n"
            f"- about_section: {{\"title\": str, \"content\": str, \"highlights\": list[str]}}\n"
            f"- services_section: {{\"title\": str, \"subtitle\": str, \"services\": list[{{\"name\": str, \"description\": str, \"icon\": str}}]}}\n"
            f"- why_us_section: {{\"title\": str, \"items\": list[str]}}\n"
            f"- gallery_section: {{\"title\": str, \"items\": list[{{\"title\": str, \"category\": str}}]}}\n"
            f"- contact_section: {{\"title\": str, \"address\": str, \"phone\": str, \"email\": str, \"hours\": str}}\n"
            f"- cta_section: {{\"heading\": str, \"subheading\": str, \"button_text\": str}}"
        )

        context_hints = {
            "business_name": lead.business_name,
            "category": lead.category,
            "location": lead.location,
            "phone": lead.phone,
            "email": lead.email,
            "variant_seed": lead.id,
            "variant_index": design_index,
        }

        generated = await self.llm_client.generate_json(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.8,
            context_hints=context_hints,
        )

        site_title = generated.get("site_title", f"{lead.business_name} | {lead.category}")
        tagline = generated.get("tagline", f"Quality {lead.category} in {lead.location}")
        hero = generated.get("hero_section", {
            "headline": f"Welcome to {lead.business_name}",
            "subheadline": f"Providing reliable {lead.category.lower()} to customers across {lead.location}.",
            "primary_cta": "Contact Us",
            "secondary_cta": "Our Services",
        })
        about = generated.get("about_section", {
            "title": f"About {lead.business_name}",
            "content": f"Serving the {lead.location} area with dedication, care, and dependable service.",
            "highlights": [f"Located conveniently in {lead.location}", "Dedicated customer care", "Professional standards"],
        })
        services = generated.get("services_section", {
            "title": "Our Services",
            "subtitle": f"Specialized {lead.category.lower()} solutions for your needs",
            "services": [
                {"name": f"Standard {lead.category} Service", "description": "High quality care tailored to client requirements.", "icon": "Sparkles"},
                {"name": "Consultations & Inquiries", "description": "Friendly expert guidance to address your questions.", "icon": "HelpCircle"},
            ],
        })
        why_us = generated.get("why_us_section", {
            "title": f"Why Choose {lead.business_name}",
            "items": ["Direct local attention", "Transparent communication", "Focused on client satisfaction"],
        })
        gallery = generated.get("gallery_section", {
            "title": "Our Work & Environment",
            "items": [{"title": "Welcoming Facility", "category": "Premises"}, {"title": "Quality Craftsmanship", "category": "Service"}],
        })
        contact = generated.get("contact_section", {
            "title": "Get in Touch",
            "address": lead.location,
            "phone": lead.phone or "Available upon request",
            "email": lead.email or "contact@localbusiness.com",
            "hours": "Monday - Saturday: 9:00 AM - 6:00 PM",
        })
        cta = generated.get("cta_section", {
            "heading": f"Connect with {lead.business_name} Today",
            "subheading": "We are ready to assist you with friendly, dependable service.",
            "button_text": "Call Now",
        })

        preview_url = f"{self.settings.dashboard_url}/preview/{lead.id}"

        full_config = {
            "business_name": lead.business_name,
            "category": lead.category,
            "location": lead.location,
            "phone": lead.phone,
            "email": lead.email,
            "color_scheme": palette,
            "design": design,
            "site_title": site_title,
            "tagline": tagline,
            "hero_section": hero,
            "about_section": about,
            "services_section": services,
            "why_us_section": why_us,
            "gallery_section": gallery,
            "contact_section": contact,
            "cta_section": cta,
            "is_prototype": True,
            "disclaimer": "AI-generated prototype concept for evaluation purposes. Not an official client website.",
        }

        # Persist prototype
        proto_stmt = select(Prototype).where(Prototype.lead_id == lead.id)
        existing_proto = (await db.execute(proto_stmt)).scalar_one_or_none()

        if existing_proto:
            existing_proto.site_title = site_title
            existing_proto.tagline = tagline
            existing_proto.color_scheme = palette
            existing_proto.hero_section = hero
            existing_proto.about_section = about
            existing_proto.services_section = services
            existing_proto.why_us_section = why_us
            existing_proto.gallery_section = gallery
            existing_proto.contact_section = contact
            existing_proto.cta_section = cta
            existing_proto.full_config = full_config
            existing_proto.preview_url = preview_url
            existing_proto.generated_at = datetime.utcnow()
            proto_record = existing_proto
        else:
            proto_record = Prototype(
                lead_id=lead.id,
                site_title=site_title,
                tagline=tagline,
                color_scheme=palette,
                hero_section=hero,
                about_section=about,
                services_section=services,
                why_us_section=why_us,
                gallery_section=gallery,
                contact_section=contact,
                cta_section=cta,
                full_config=full_config,
                preview_url=preview_url,
                generated_at=datetime.utcnow(),
            )
            db.add(proto_record)

        lead.status = "WEBSITE_READY"
        await db.commit()
        await db.refresh(proto_record)

        logger.info("Generated prototype for '%s' (preview: %s)", lead.business_name, preview_url)
        return full_config, (analysis.source_urls if analysis else lead.source_urls)
