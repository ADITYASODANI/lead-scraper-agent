"""
Agent 1: Lead Discovery Agent.
Discovers potential businesses across target categories and locations using Playwright
normalizes fields, and enforces strict multi-key deduplication.
"""

from datetime import datetime
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.agents.base import BaseAgent
from app.models import Lead
from app.services.scraper_service import ScraperService

logger = logging.getLogger(__name__)


def normalize_string(val: Optional[str]) -> str:
    """Normalize string for consistent deduplication comparisons."""
    if not val:
        return ""
    return "".join(c for c in val.lower() if c.isalnum())


class LeadDiscoveryAgent(BaseAgent):
    """Lead Discovery Agent: searches public directories and deduplicates leads."""

    def __init__(self):
        super().__init__(name="lead_discovery_agent")
        self.scraper_service = ScraperService()

    async def _run(
        self,
        db: AsyncSession,
        input_data: Dict[str, Any],
        lead_id: Optional[str] = None,
    ) -> tuple[List[Dict[str, Any]], List[str]]:
        category = input_data.get("category", "Restaurants")
        location = input_data.get("location", "Downtown, CA")
        max_leads = int(input_data.get("max_leads", 5))

        logger.info("Executing discovery for '%s' in '%s' (max=%d)", category, location, max_leads)

        # Step 1: Collect raw leads
        raw_leads = await self.scraper_service.scrape_google_maps(
            query=category, location=location, max_results=max_leads
        )

        persisted_leads = []
        source_urls = []

        # Step 2: Deduplication and persistence
        for raw in raw_leads:
            name = (raw.get("business_name") or "").strip()
            loc = (raw.get("location") or location).strip()
            phone = (raw.get("phone") or "").strip()
            website = (raw.get("website") or "").strip()
            place_id = raw.get("place_id")

            if not name:
                continue

            # Query existing leads to check duplicates
            is_dup = await self._is_duplicate(db, name, loc, phone, website, place_id)
            if is_dup:
                logger.info("Skipping duplicate lead: '%s' (%s)", name, loc)
                continue

            new_lead = Lead(
                business_name=name,
                category=category.title(),
                description=raw.get("description"),
                location=loc,
                phone=phone or None,
                email=raw.get("email") or None,
                website=website or None,
                social_links=raw.get("social_links") or [],
                source_urls=raw.get("source_urls") or [],
                place_id=place_id,
                status="DISCOVERED",
                review_status="PENDING",
                created_at=datetime.utcnow(),
            )
            db.add(new_lead)
            await db.flush()
            await db.refresh(new_lead)

            persisted_leads.append({
                "lead_id": new_lead.id,
                "business_name": new_lead.business_name,
                "category": new_lead.category,
                "location": new_lead.location,
                "phone": new_lead.phone,
                "email": new_lead.email,
                "website": new_lead.website,
                "status": new_lead.status,
            })
            source_urls.extend(new_lead.source_urls)

        await db.commit()
        logger.info("Discovery completed. Saved %d new non-duplicate leads.", len(persisted_leads))
        return persisted_leads, list(set(source_urls))

    async def _is_duplicate(
        self,
        db: AsyncSession,
        name: str,
        location: str,
        phone: str,
        website: str,
        place_id: Optional[str],
    ) -> bool:
        """
        Check if business lead already exists using place_id, phone, website,
        or fuzzy name + location match.
        """
        conditions = []
        if place_id:
            conditions.append(Lead.place_id == place_id)
        if phone:
            conditions.append(Lead.phone == phone)
        if website:
            conditions.append(Lead.website == website)

        # Exact name and location check
        conditions.append(
            (Lead.business_name == name) & (Lead.location == location)
        )

        stmt = select(Lead.id).where(or_(*conditions)).limit(1)
        res = await db.execute(stmt)
        return res.scalar_one_or_none() is not None
