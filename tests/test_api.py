"""
Integration tests for FastAPI REST API endpoints.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import get_db


@pytest.mark.asyncio
async def test_health_check_endpoint():
    """Verify system health check."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


@pytest.mark.asyncio
async def test_stats_and_leads_endpoints(test_db_session):
    """Verify listing leads, stats, and scheduler status."""
    async def override_get_db():
        yield test_db_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Check initial stats
            stats_res = await client.get("/api/stats")
            assert stats_res.status_code == 200
            stats = stats_res.json()
            assert "total_leads" in stats
            assert "qualified" in stats

            # Check scheduler endpoint
            sched_res = await client.get("/api/pipeline/scheduler")
            assert sched_res.status_code == 200
            sched = sched_res.json()
            assert "interval_hours" in sched

            # Check update scheduler
            update_res = await client.post(
                "/api/pipeline/scheduler",
                json={"interval_hours": 8, "enabled": True},
            )
            assert update_res.status_code == 200
            assert update_res.json()["scheduler"]["interval_hours"] == 8

            # Check leads listing
            leads_res = await client.get("/api/leads")
            assert leads_res.status_code == 200
            assert isinstance(leads_res.json(), list)
    finally:
        app.dependency_overrides.clear()
