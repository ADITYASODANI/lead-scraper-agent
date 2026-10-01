"""
Leads API Router.
Handles lead listing, filtering, detail retrieval, review status approval/rejection,
and manual edits.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, desc, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models import Lead, BusinessAnalysis, Opportunity, Prototype, Pitch, AgentRun
from app.schemas import (
    LeadResponse,
    LeadDetailResponse,
    LeadUpdate,
    ReviewStatusUpdate,
)

router = APIRouter(prefix="/leads", tags=["Leads"])


@router.get("", response_model=List[LeadResponse])
async def list_leads(
    status: Optional[str] = Query(None, description="Filter by workflow status"),
    review_status: Optional[str] = Query(None, description="Filter by review status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search by business name or location"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List business leads with optional filtering and pagination."""
    query = (
        select(Lead)
        .options(
            selectinload(Lead.analysis),
            selectinload(Lead.opportunity),
            selectinload(Lead.prototype),
            selectinload(Lead.pitch),
        )
        .order_by(desc(Lead.created_at))
        .offset(offset)
        .limit(limit)
    )

    if status:
        query = query.where(Lead.status == status)
    if review_status:
        query = query.where(Lead.review_status == review_status)
    if category:
        query = query.where(Lead.category == category)
    if search:
        search_fmt = f"%{search.strip()}%"
        query = query.where(
            or_(
                Lead.business_name.ilike(search_fmt),
                Lead.location.ilike(search_fmt),
            )
        )

    results = (await db.execute(query)).scalars().all()

    lead_responses = []
    for lead in results:
        analysis_status = lead.analysis.website_status if lead.analysis else None
        qualified = lead.opportunity.qualified if lead.opportunity else None
        priority = lead.opportunity.priority if lead.opportunity else None
        confidence = lead.opportunity.confidence if lead.opportunity else None
        has_proto = lead.prototype is not None
        has_pitch = lead.pitch is not None

        lead_responses.append(
            LeadResponse(
                id=lead.id,
                business_name=lead.business_name,
                category=lead.category,
                description=lead.description,
                location=lead.location,
                phone=lead.phone,
                email=lead.email,
                website=lead.website,
                social_links=lead.social_links or [],
                source_urls=lead.source_urls or [],
                place_id=lead.place_id,
                status=lead.status,
                review_status=lead.review_status,
                notes=lead.notes,
                created_at=lead.created_at,
                updated_at=lead.updated_at,
                analysis_status=analysis_status,
                qualified=qualified,
                priority=priority,
                confidence=confidence,
                has_prototype=has_proto,
                has_pitch=has_pitch,
            )
        )

    return lead_responses


@router.get("/{lead_id}", response_model=LeadDetailResponse)
async def get_lead_detail(lead_id: str, db: AsyncSession = Depends(get_db)):
    """Fetch complete dossier for a lead, including all agent deliverables and audit runs."""
    stmt = (
        select(Lead)
        .where(Lead.id == lead_id)
        .options(
            selectinload(Lead.analysis),
            selectinload(Lead.opportunity),
            selectinload(Lead.prototype),
            selectinload(Lead.pitch),
            selectinload(Lead.agent_runs),
        )
    )
    lead = (await db.execute(stmt)).scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    return LeadDetailResponse(
        id=lead.id,
        business_name=lead.business_name,
        category=lead.category,
        description=lead.description,
        location=lead.location,
        phone=lead.phone,
        email=lead.email,
        website=lead.website,
        social_links=lead.social_links or [],
        source_urls=lead.source_urls or [],
        place_id=lead.place_id,
        status=lead.status,
        review_status=lead.review_status,
        notes=lead.notes,
        created_at=lead.created_at,
        updated_at=lead.updated_at,
        analysis=lead.analysis,
        opportunity=lead.opportunity,
        prototype=lead.prototype,
        pitch=lead.pitch,
        agent_runs=lead.agent_runs or [],
        analysis_status=lead.analysis.website_status if lead.analysis else None,
        qualified=lead.opportunity.qualified if lead.opportunity else None,
        priority=lead.opportunity.priority if lead.opportunity else None,
        confidence=lead.opportunity.confidence if lead.opportunity else None,
        has_prototype=lead.prototype is not None,
        has_pitch=lead.pitch is not None,
    )


@router.patch("/{lead_id}/review", response_model=LeadResponse)
async def update_review_status(
    lead_id: str,
    update: ReviewStatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Human review decision action.
    Updates status to PENDING, APPROVED, REJECTED, or CONTACTED.
    """
    stmt = (
        select(Lead)
        .where(Lead.id == lead_id)
        .options(
            selectinload(Lead.analysis),
            selectinload(Lead.opportunity),
            selectinload(Lead.prototype),
            selectinload(Lead.pitch),
        )
    )
    lead = (await db.execute(stmt)).scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    lead.review_status = update.review_status
    if update.notes is not None:
        lead.notes = update.notes

    await db.commit()
    await db.refresh(lead)

    return LeadResponse(
        id=lead.id,
        business_name=lead.business_name,
        category=lead.category,
        description=lead.description,
        location=lead.location,
        phone=lead.phone,
        email=lead.email,
        website=lead.website,
        social_links=lead.social_links or [],
        source_urls=lead.source_urls or [],
        place_id=lead.place_id,
        status=lead.status,
        review_status=lead.review_status,
        notes=lead.notes,
        created_at=lead.created_at,
        updated_at=lead.updated_at,
        analysis_status=lead.analysis.website_status if lead.analysis else None,
        qualified=lead.opportunity.qualified if lead.opportunity else None,
        priority=lead.opportunity.priority if lead.opportunity else None,
        confidence=lead.opportunity.confidence if lead.opportunity else None,
        has_prototype=lead.prototype is not None,
        has_pitch=lead.pitch is not None,
    )


@router.patch("/{lead_id}", response_model=LeadResponse)
async def update_lead_details(
    lead_id: str,
    update: LeadUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update lead contact information or internal review notes."""
    stmt = (
        select(Lead)
        .where(Lead.id == lead_id)
        .options(
            selectinload(Lead.analysis),
            selectinload(Lead.opportunity),
            selectinload(Lead.prototype),
            selectinload(Lead.pitch),
        )
    )
    lead = (await db.execute(stmt)).scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    for field, val in update.model_dump(exclude_unset=True).items():
        setattr(lead, field, val)

    await db.commit()
    await db.refresh(lead)

    return LeadResponse(
        id=lead.id,
        business_name=lead.business_name,
        category=lead.category,
        description=lead.description,
        location=lead.location,
        phone=lead.phone,
        email=lead.email,
        website=lead.website,
        social_links=lead.social_links or [],
        source_urls=lead.source_urls or [],
        place_id=lead.place_id,
        status=lead.status,
        review_status=lead.review_status,
        notes=lead.notes,
        created_at=lead.created_at,
        updated_at=lead.updated_at,
        analysis_status=lead.analysis.website_status if lead.analysis else None,
        qualified=lead.opportunity.qualified if lead.opportunity else None,
        priority=lead.opportunity.priority if lead.opportunity else None,
        confidence=lead.opportunity.confidence if lead.opportunity else None,
        has_prototype=lead.prototype is not None,
        has_pitch=lead.pitch is not None,
    )


@router.delete("/{lead_id}")
async def delete_lead(lead_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a lead and all cascaded deliverables."""
    stmt = select(Lead).where(Lead.id == lead_id)
    lead = (await db.execute(stmt)).scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    await db.delete(lead)
    await db.commit()
    return {"status": "success", "message": f"Lead '{lead.business_name}' deleted."}
