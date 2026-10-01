"""
Scraper and HTTP Probing Service.
Includes SSRF-safe HTTP inspection, metadata extraction, Playwright Google Maps scraping,
and lead scraping.
"""

import asyncio
import ipaddress
import logging
import re
import socket
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse, quote_plus
from bs4 import BeautifulSoup
import httpx
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from app.config import get_settings

logger = logging.getLogger(__name__)


def is_safe_url(url: str) -> bool:
    """
    Validate that the URL does not resolve to private, loopback, or cloud metadata IP addresses
    to prevent Server-Side Request Forgery (SSRF).
    """
    if not url:
        return False
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False
        hostname = parsed.hostname
        if not hostname:
            return False

        # Disallow loopback / special names
        if hostname.lower() in ("localhost", "metadata.google.internal"):
            return False

        # Resolve hostname
        ip_addresses = socket.gethostbyname_ex(hostname)[2]
        for ip_str in ip_addresses:
            ip = ipaddress.ip_address(ip_str)
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                return False
        return True
    except Exception as exc:
        logger.debug("URL safety verification failed for %s: %s", url, exc)
        return False


class ScraperService:
    """Service for deterministic website probing and Google Maps lead scraping."""

    def __init__(self):
        self.settings = get_settings()

    async def probe_website(self, url: Optional[str]) -> Dict[str, Any]:
        """
        Deterministically inspect a business website without invoking an LLM.
        Checks HTTP status, SSL, mobile viewport, title, and response time.
        """
        if not url or not url.strip():
            return {
                "website_status": "MISSING",
                "accessible": False,
                "status_code": None,
                "has_https": False,
                "has_viewport": False,
                "title": "",
                "meta_description": "",
                "response_time_ms": None,
                "issues": ["No website URL provided in business listing"],
            }

        clean_url = url.strip()
        if not clean_url.startswith(("http://", "https://")):
            clean_url = "https://" + clean_url

        if not is_safe_url(clean_url):
            return {
                "website_status": "UNKNOWN",
                "accessible": False,
                "status_code": None,
                "has_https": clean_url.startswith("https://"),
                "has_viewport": False,
                "title": "",
                "meta_description": "",
                "response_time_ms": None,
                "issues": ["Target URL blocked by security policy (private/invalid address)"],
            }

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
        }

        try:
            async with httpx.AsyncClient(
                timeout=12.0, follow_redirects=True, verify=False
            ) as client:
                response = await client.get(clean_url, headers=headers)
                elapsed_ms = round(response.elapsed.total_seconds() * 1000, 2)

                if response.status_code >= 400:
                    return {
                        "website_status": "NEEDS_IMPROVEMENT",
                        "accessible": False,
                        "status_code": response.status_code,
                        "has_https": str(response.url).startswith("https://"),
                        "has_viewport": False,
                        "title": "",
                        "meta_description": "",
                        "response_time_ms": elapsed_ms,
                        "issues": [f"Website returned HTTP error status code {response.status_code}"],
                    }

                # Parse HTML
                soup = BeautifulSoup(response.text, "html.parser")
                title = soup.title.string.strip() if soup.title and soup.title.string else ""
                meta_desc = ""
                desc_tag = soup.find("meta", attrs={"name": re.compile(r"description", re.I)})
                if desc_tag and desc_tag.get("content"):
                    meta_desc = desc_tag["content"].strip()

                viewport_tag = soup.find("meta", attrs={"name": re.compile(r"viewport", re.I)})
                has_viewport = bool(viewport_tag)

                issues = []
                if not str(response.url).startswith("https://"):
                    issues.append("Site is not served over secure HTTPS")
                if not has_viewport:
                    issues.append("Missing mobile viewport meta tag (poor smartphone experience)")
                if elapsed_ms > 4000:
                    issues.append(f"Slow response latency ({elapsed_ms}ms)")
                if not title:
                    issues.append("Missing HTML page title tag")

                status = "NEEDS_IMPROVEMENT" if issues else "PRESENT"

                return {
                    "website_status": status,
                    "accessible": True,
                    "status_code": response.status_code,
                    "has_https": str(response.url).startswith("https://"),
                    "has_viewport": has_viewport,
                    "title": title,
                    "meta_description": meta_desc,
                    "response_time_ms": elapsed_ms,
                    "issues": issues,
                }

        except Exception as exc:
            logger.info("Probe failed for %s: %s", clean_url, exc)
            return {
                "website_status": "MISSING",
                "accessible": False,
                "status_code": None,
                "has_https": clean_url.startswith("https://"),
                "has_viewport": False,
                "title": "",
                "meta_description": "",
                "response_time_ms": None,
                "issues": [f"Website unreachable or connection failed: {str(exc)}"],
            }

    async def scrape_google_maps(
        self, query: str, location: str, max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Scrape public business leads from Google Maps using Playwright.
        Returns an empty list if browser execution fails or finds nothing.
        """
        full_query = f"{query} in {location}"
        search_url = f"https://www.google.com/maps/search/{quote_plus(full_query)}"
        leads: List[Dict[str, Any]] = []

        try:
            async with async_playwright() as pw:
                browser = await pw.chromium.launch(
                    headless=self.settings.scraper_headless,
                    args=["--no-sandbox", "--disable-dev-shm-usage"],
                )
                context = await browser.new_context(
                    viewport={"width": 1280, "height": 800},
                    user_agent=(
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
                    ),
                )
                page = await context.new_page()

                logger.info("Navigating to Google Maps search: %s", search_url)
                await page.goto(search_url, timeout=self.settings.scraper_timeout_ms, wait_until="domcontentloaded")
                await asyncio.sleep(2.0)

                # Attempt to handle cookie consent dialog if present
                for btn_text in ["Accept all", "Reject all", "Agree", "I agree"]:
                    try:
                        btn = page.locator(f"button:has-text('{btn_text}')").first
                        if await btn.is_visible(timeout=1000):
                            await btn.click()
                            await asyncio.sleep(1.0)
                            break
                    except Exception:
                        pass

                # Scroll feed to load items
                feed_selector = 'div[role="feed"]'
                try:
                    feed = page.locator(feed_selector).first
                    if await feed.is_visible(timeout=3000):
                        for _ in range(3):
                            await feed.evaluate("node => node.scrollTop += 800")
                            await asyncio.sleep(1.0)
                except Exception:
                    pass

                # Extract business elements
                elements = await page.locator('div[role="feed"] > div > div[jsaction]').all()
                if not elements:
                    elements = await page.locator('a[href*="/maps/place/"]').all()

                logger.info("Found %d raw business elements on Google Maps", len(elements))

                for elem in elements[:max_results * 2]:
                    if len(leads) >= max_results:
                        break
                    try:
                        text = await elem.inner_text()
                        lines = [line.strip() for line in text.split("\n") if line.strip()]
                        if not lines:
                            continue

                        name = lines[0]
                        # Filter out non-business labels
                        if name in ("Results", "Sponsored", "Ad", "Directions", "Website"):
                            continue
                        # Skip the Maps filter bar (e.g. "PriceRatingHoursAll filters")
                        if "filters" in name.lower():
                            continue

                        # Extract details from text
                        phone_match = re.search(r"(\+?\d{1,3}[\s-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}", text)
                        phone = phone_match.group(0) if phone_match else None

                        website = None
                        website_elem = elem.locator('a[href^="http"]').first
                        if await website_elem.count() > 0:
                            href = await website_elem.get_attribute("href")
                            if href and "google.com" not in href:
                                website = href

                        # Direct Google Maps place link (photos, menu, reviews)
                        place_url = await elem.get_attribute("href")
                        if not place_url or "/maps/place/" not in place_url:
                            place_link = elem.locator('a[href*="/maps/place/"]').first
                            place_url = (
                                await place_link.get_attribute("href")
                                if await place_link.count() > 0 else None
                            )

                        leads.append({
                            "business_name": name,
                            "category": query.title(),
                            "location": location,
                            "phone": phone,
                            "email": None,
                            "website": website,
                            "description": f"Local {query.lower()} operating in {location}",
                            "social_links": [],
                            "source_urls": [place_url, search_url] if place_url else [search_url],
                            "place_id": f"gmap_{abs(hash(name + location))}",
                        })
                    except Exception as err:
                        logger.debug("Failed parsing lead item: %s", err)

                await browser.close()

        except Exception as exc:
            logger.warning("Playwright Google Maps scraping failed or timed out: %s", exc)

        return leads[:max_results]
