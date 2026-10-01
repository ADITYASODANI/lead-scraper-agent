"""
Unit and integration tests for all 5 Agents in the pipeline.
"""

import pytest
from app.agents import (
    LeadDiscoveryAgent,
    BusinessAnalysisAgent,
    OpportunityValidatorAgent,
    WebsiteGeneratorAgent,
    PitchGeneratorAgent,
)
from app.models import Lead, BusinessAnalysis, Opportunity, Prototype, Pitch


@pytest.mark.asyncio
async def test_lead_discovery_and_deduplication(test_db_session):
    """Test Agent 1: Lead discovery and multi-key deduplication."""
    agent = LeadDiscoveryAgent()

    # Run discovery (scraper stubbed in conftest)
    result = await agent.execute(
        db=test_db_session,
        input_data={
            "category": "Gym",
            "location": "Denver, CO",
            "max_leads": 3,
        },
    )

    assert result.status == "SUCCESS"
    assert len(result.data) == 3
    first_lead = result.data[0]
    assert "lead_id" in first_lead
    assert first_lead["category"] == "Gym"

    # Run again with same parameters - should detect duplicates and add 0 new leads
    dup_result = await agent.execute(
        db=test_db_session,
        input_data={
            "category": "Gym",
            "location": "Denver, CO",
            "max_leads": 3,
        },
    )
    assert dup_result.status == "SUCCESS"
    assert len(dup_result.data) == 0  # All were duplicates!


@pytest.mark.asyncio
async def test_business_analysis_missing_website(test_db_session):
    """Test Agent 2: Analysis of a business with NO website."""
    lead = Lead(
        business_name="Rustic Wood Fired Pizza",
        category="Restaurant",
        location="Seattle, WA",
        phone="+1 206 555 1234",
        website=None,
        status="DISCOVERED",
    )
    test_db_session.add(lead)
    await test_db_session.commit()
    await test_db_session.refresh(lead)

    agent = BusinessAnalysisAgent()
    result = await agent.execute(db=test_db_session, input_data={}, lead_id=lead.id)

    assert result.status == "SUCCESS"
    data = result.data
    assert data["websiteStatus"] in ("MISSING", "NEEDS_IMPROVEMENT")
    assert data["websiteOpportunity"] is True
    assert len(data["observations"]) > 0
    assert len(data["evidence"]) > 0

    await test_db_session.refresh(lead)
    assert lead.status == "ANALYZED"


@pytest.mark.asyncio
async def test_opportunity_validator_qualifies(test_db_session):
    """Test Agent 3: Opportunity validator properly qualifies viable business."""
    lead = Lead(
        business_name="Downtown Dental Care",
        category="Dental Clinic",
        location="Austin, TX",
        phone="+1 512 555 9876",
        website=None,
        status="ANALYZED",
    )
    test_db_session.add(lead)
    await test_db_session.flush()

    analysis = BusinessAnalysis(
        lead_id=lead.id,
        website_status="MISSING",
        business_summary="Local dental clinic offering routine exams and cleaning.",
        current_digital_presence="Phone-only inquiries.",
        observations=["No website found on public profiles"],
        missing_features=["Online booking", "Service list"],
        website_opportunity=True,
        evidence=["No registered domain on Google Maps"],
    )
    test_db_session.add(analysis)
    await test_db_session.commit()

    agent = OpportunityValidatorAgent()
    result = await agent.execute(db=test_db_session, input_data={}, lead_id=lead.id)

    assert result.status == "SUCCESS"
    data = result.data
    assert data["qualified"] is True
    assert data["priority"] in ("HIGH", "MEDIUM", "LOW")
    assert 0.0 <= data["confidence"] <= 1.0
    assert len(data["reasoning"]) > 0

    await test_db_session.refresh(lead)
    assert lead.status == "QUALIFIED"


@pytest.mark.asyncio
async def test_opportunity_validator_disqualifies_complete_website(test_db_session):
    """Test Agent 3: Early rejection when a business already has a working complete website."""
    lead = Lead(
        business_name="Mega Gym Corp",
        category="Gym",
        location="Chicago, IL",
        phone="+1 312 555 1111",
        website="https://example.com",
        status="ANALYZED",
    )
    test_db_session.add(lead)
    await test_db_session.flush()

    analysis = BusinessAnalysis(
        lead_id=lead.id,
        website_status="PRESENT",
        business_summary="Large franchise with full online membership portal.",
        current_digital_presence="Complete digital presence.",
        observations=["Fully functioning website with mobile responsiveness"],
        missing_features=[],
        website_opportunity=False,  # No opportunity!
        evidence=["Modern site already exists"],
    )
    test_db_session.add(analysis)
    await test_db_session.commit()

    agent = OpportunityValidatorAgent()
    result = await agent.execute(db=test_db_session, input_data={}, lead_id=lead.id)

    assert result.status == "SUCCESS"
    assert result.data["qualified"] is False

    await test_db_session.refresh(lead)
    assert lead.status == "REJECTED"


@pytest.mark.asyncio
async def test_website_generator_prototype(test_db_session):
    """Test Agent 4: Generates prototype with all required sections and no fake data."""
    lead = Lead(
        business_name="Soleil Hair Salon",
        category="Salon",
        location="Miami, FL",
        phone="+1 305 555 4321",
        email="hello@soleilsalon.com",
        website=None,
        status="QUALIFIED",
    )
    test_db_session.add(lead)
    await test_db_session.flush()

    opp = Opportunity(
        lead_id=lead.id,
        qualified=True,
        opportunity_type="SINGLE_PAGE_WEBSITE",
        priority="HIGH",
        confidence=0.9,
        recommended_solution="Clean salon landing page with style gallery and phone booking",
    )
    test_db_session.add(opp)
    await test_db_session.commit()

    agent = WebsiteGeneratorAgent()
    result = await agent.execute(db=test_db_session, input_data={}, lead_id=lead.id)

    assert result.status == "SUCCESS"
    cfg = result.data
    assert "hero_section" in cfg
    assert "about_section" in cfg
    assert "services_section" in cfg
    assert "why_us_section" in cfg
    assert "gallery_section" in cfg
    assert "contact_section" in cfg
    assert "cta_section" in cfg
    assert "color_scheme" in cfg

    await test_db_session.refresh(lead)
    assert lead.status == "WEBSITE_READY"


@pytest.mark.asyncio
async def test_pitch_generator_three_variants(test_db_session):
    """Test Agent 5: Pitch generator outputs WhatsApp, Email, and Detailed formats."""
    lead = Lead(
        business_name="Soleil Hair Salon",
        category="Salon",
        location="Miami, FL",
        phone="+1 305 555 4321",
        status="WEBSITE_READY",
    )
    test_db_session.add(lead)
    await test_db_session.flush()

    analysis = BusinessAnalysis(
        lead_id=lead.id,
        website_status="MISSING",
        business_summary="Local hair styling salon.",
        current_digital_presence="Phone only.",
        observations=["Missing official mobile website"],
        missing_features=["Service list"],
        website_opportunity=True,
    )
    test_db_session.add(analysis)

    proto = Prototype(
        lead_id=lead.id,
        site_title="Soleil Hair Salon",
        tagline="Chic styling in Miami",
        preview_url="http://localhost:5173/preview/test-id",
    )
    test_db_session.add(proto)
    await test_db_session.commit()

    agent = PitchGeneratorAgent()
    result = await agent.execute(db=test_db_session, input_data={}, lead_id=lead.id)

    assert result.status == "SUCCESS"
    data = result.data
    assert "short_pitch" in data
    assert "email_pitch" in data
    assert "detailed_pitch" in data
    assert "http://localhost:5173/preview/test-id" in data["short_pitch"]
    assert "Soleil Hair Salon" in data["email_pitch"]

    await test_db_session.refresh(lead)
    assert lead.status == "HUMAN_REVIEW"
    assert lead.review_status == "PENDING"
