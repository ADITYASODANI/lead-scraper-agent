"""
End-to-End Orchestrator and Pipeline Integration Tests.
"""

import pytest
from sqlalchemy import select
from app.services.orchestrator import PipelineOrchestrator
from app.models import Lead, Prototype, Pitch


@pytest.mark.asyncio
async def test_end_to_end_pipeline_flow(test_db_session):
    """Test full sequential workflow execution."""
    orchestrator = PipelineOrchestrator()

    result = await orchestrator.run_pipeline(
        db=test_db_session,
        category="Cafe",
        location="Portland, OR",
        max_leads=2,
    )

    assert result["status"] == "success"
    stats = result["stats"]
    assert stats["leads_discovered"] == 2
    assert stats["leads_processed"] == 2

    # Check database state
    leads = (await test_db_session.execute(select(Lead))).scalars().all()
    assert len(leads) == 2

    for lead in leads:
        if lead.status == "HUMAN_REVIEW":
            # Must have prototype and pitch
            proto = (await test_db_session.execute(
                select(Prototype).where(Prototype.lead_id == lead.id)
            )).scalar_one_or_none()
            assert proto is not None

            pitch = (await test_db_session.execute(
                select(Pitch).where(Pitch.lead_id == lead.id)
            )).scalar_one_or_none()
            assert pitch is not None
            assert lead.review_status == "PENDING"
