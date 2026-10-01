"""
Dashboard Statistics API Router.
Calculates real-time aggregate KPIs for the system overview.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Lead, Opportunity, Prototype, Pitch
from app.schemas import DashboardStats

router = APIRouter(prefix="/stats", tags=["Dashboard Statistics"])


@router.get("", response_model=DashboardStats)
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """Aggregate high-level pipeline and review metrics."""
    # Total leads
    total_leads = (await db.execute(select(func.count(Lead.id)))).scalar() or 0

    # New leads (just discovered, not yet analyzed)
    new_leads = (await db.execute(
        select(func.count(Lead.id)).where(Lead.status == "DISCOVERED")
    )).scalar() or 0

    # Analyzed leads (status is not DISCOVERED and not ANALYZING)
    analyzed = (await db.execute(
        select(func.count(Lead.id)).where(~Lead.status.in_(["DISCOVERED", "ANALYZING"]))
    )).scalar() or 0

    # Qualified count
    qualified = (await db.execute(
        select(func.count(Opportunity.id)).where(Opportunity.qualified == True)  # noqa: E712
    )).scalar() or 0

    # Rejected count
    rejected = (await db.execute(
        select(func.count(Lead.id)).where(Lead.status == "REJECTED")
    )).scalar() or 0

    # Websites generated
    websites = (await db.execute(select(func.count(Prototype.id)))).scalar() or 0

    # Pitches ready
    pitches = (await db.execute(select(func.count(Pitch.id)))).scalar() or 0

    # Human review statuses
    approved = (await db.execute(
        select(func.count(Lead.id)).where(Lead.review_status == "APPROVED")
    )).scalar() or 0

    contacted = (await db.execute(
        select(func.count(Lead.id)).where(Lead.review_status == "CONTACTED")
    )).scalar() or 0

    return DashboardStats(
        total_leads=total_leads,
        new_leads=new_leads,
        analyzed=analyzed,
        qualified=qualified,
        rejected=rejected,
        websites_generated=websites,
        pitches_ready=pitches,
        approved=approved,
        contacted=contacted,
    )
