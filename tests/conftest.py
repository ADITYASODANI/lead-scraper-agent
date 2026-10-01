"""
Test fixtures and configuration.
Uses in-memory SQLite database and test event loop.
"""

import sys
from pathlib import Path
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Add backend directory to sys.path
backend_path = Path(__file__).resolve().parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.models import Base
from app.config import get_settings

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def test_db_session() -> AsyncSession:
    """Creates a fresh in-memory database session for each test."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )

    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture(autouse=True)
def stub_scraper(monkeypatch):
    """Replace live Google Maps scraping with deterministic leads for tests."""
    from app.services.scraper_service import ScraperService

    async def fake_scrape(self, query, location, max_results=5):
        return [
            {
                "business_name": f"Test {query.title()} {i}",
                "location": location,
                "phone": f"+1 555 000 {1000 + i}",
                "website": None,
                "description": f"Test {query} in {location}",
                "social_links": [],
                "source_urls": [],
                "place_id": f"test_{query}_{location}_{i}",
            }
            for i in range(max_results)
        ]

    monkeypatch.setattr(ScraperService, "scrape_google_maps", fake_scrape)
