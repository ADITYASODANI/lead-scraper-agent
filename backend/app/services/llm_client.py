"""
Unified Multi-Provider LLM Client.
Supports Groq, OpenRouter, OpenAI, Ollama, and an intelligent Mock Provider.
Includes automatic fallback, JSON parsing/repair, and strict schema compliance.
"""

import json
import logging
import re
from typing import Optional, Dict, Any
import httpx
from app.config import get_settings
from app.services.mock_site_copy import build_mock_website_copy

logger = logging.getLogger(__name__)


class LLMClient:
    """Multi-provider LLM interface with fallback and JSON parsing."""

    def __init__(self):
        self.settings = get_settings()
        self.provider = (self.settings.llm_provider or "mock").lower()
        self.api_key = self.settings.llm_api_key
        self.model = self.settings.llm_model
        self.fallback_to_mock = self.settings.llm_fallback_to_mock

    async def generate_json(
        self,
        prompt: str,
        system_prompt: str,
        temperature: float = 0.2,
        context_hints: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Request JSON output from the active LLM provider.
        Falls back to Mock provider if primary provider fails and fallback is enabled.
        """
        if self.provider == "mock" or not self.api_key:
            return self._generate_mock_json(prompt, context_hints)

        try:
            if self.provider == "groq":
                return await self._call_groq(prompt, system_prompt, temperature)
            elif self.provider in ("openai", "openrouter"):
                return await self._call_openai_compatible(prompt, system_prompt, temperature)
            elif self.provider == "ollama":
                return await self._call_ollama(prompt, system_prompt, temperature)
            else:
                logger.warning("Unsupported LLM provider '%s', using mock fallback", self.provider)
                return self._generate_mock_json(prompt, context_hints)
        except Exception as exc:
            logger.warning("LLM call to %s failed: %s", self.provider, exc)
            if self.fallback_to_mock:
                logger.info("Falling back to intelligent Mock LLM generation")
                return self._generate_mock_json(prompt, context_hints)
            raise

    async def _call_groq(self, prompt: str, system_prompt: str, temperature: float) -> Dict[str, Any]:
        """Call Groq API with JSON object mode."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model or "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": f"{system_prompt}\nReturn ONLY valid JSON."},
                {"role": "user", "content": prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": temperature,
            "max_tokens": 1500,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            return self._parse_json_safely(content)

    async def _call_openai_compatible(self, prompt: str, system_prompt: str, temperature: float) -> Dict[str, Any]:
        """Call OpenAI or OpenRouter compatible completions endpoint."""
        url = (
            "https://openrouter.ai/api/v1/chat/completions"
            if self.provider == "openrouter"
            else "https://api.openai.com/v1/chat/completions"
        )
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model or ("meta-llama/llama-3.3-70b-instruct" if self.provider == "openrouter" else "gpt-4o-mini"),
            "messages": [
                {"role": "system", "content": f"{system_prompt}\nReturn ONLY a valid JSON object."},
                {"role": "user", "content": prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": temperature,
            "max_tokens": 1500,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            return self._parse_json_safely(content)

    async def _call_ollama(self, prompt: str, system_prompt: str, temperature: float) -> Dict[str, Any]:
        """Call local Ollama endpoint."""
        payload = {
            "model": self.model or "llama3",
            "messages": [
                {"role": "system", "content": f"{system_prompt}\nOutput strict JSON."},
                {"role": "user", "content": prompt},
            ],
            "format": "json",
            "stream": False,
            "options": {"temperature": temperature},
        }
        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post("http://localhost:11434/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()
            content = data["message"]["content"]
            return self._parse_json_safely(content)

    def _parse_json_safely(self, text: str) -> Dict[str, Any]:
        """Sanitize and parse JSON string from LLM responses."""
        text = text.strip()
        # Remove Markdown code blocks if present
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
        return json.loads(text)

    def _generate_mock_json(
        self, prompt: str, context_hints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate realistic, context-aware mock JSON for zero-cost testing, demo mode,
        or automatic fallback.
        """
        hints = context_hints or {}
        business_name = hints.get("business_name", "Local Business")
        category = hints.get("category", "General Services")
        location = hints.get("location", "Local Area")
        phone = hints.get("phone", "+1 (555) 019-2831")

        # Detect intent from prompt
        lower_prompt = prompt.lower()

        # Intent 1: Business Analysis
        if "analyze" in lower_prompt or "website_status" in lower_prompt:
            return {
                "businessName": business_name,
                "websiteStatus": "MISSING" if not hints.get("website") else "NEEDS_IMPROVEMENT",
                "businessSummary": f"{business_name} is an established local {category.lower()} in {location}, serving walk-in and phone-in customers.",
                "currentDigitalPresence": "Relying strictly on Google Maps listing and word-of-mouth. Lacks an official website or mobile portal.",
                "observations": [
                    f"No direct web domain linked on public search profiles for {business_name}",
                    f"Customers currently have to call {phone} to inquire about hours, offerings, and pricing",
                    "Competitors in the immediate area feature modern landing pages with digital menus/catalogs",
                ],
                "missingFeatures": [
                    "Mobile-optimized showcase of primary services and packages",
                    "Direct click-to-call and WhatsApp quick inquiry button",
                    "Interactive Google Maps location and directions banner",
                    "Clear operating hours and FAQ section",
                ],
                "websiteOpportunity": True,
                "evidence": [
                    "Public listing contains valid phone and address but no website URL",
                    "Search query for exact business name yielded no dedicated company domain",
                ],
                "sourceUrls": hints.get("source_urls", [f"https://www.google.com/maps/search/{business_name}"]),
            }

        # Intent 2: Opportunity Validation
        if "validate" in lower_prompt or "qualified" in lower_prompt:
            has_website = bool(hints.get("website"))
            return {
                "qualified": True,
                "opportunityType": "SINGLE_PAGE_WEBSITE",
                "priority": "HIGH" if not has_website else "MEDIUM",
                "confidence": 0.88,
                "reasoning": [
                    f"High consumer demand in {location} for {category.lower()}",
                    "Clear deficit in digital discovery without an official landing page",
                    "Fast turnaround single-page prototype will offer immediate customer conversion impact",
                ],
                "evidence": [
                    f"Verified physical presence in {location}",
                    "No functional web landing page present",
                ],
                "recommendedSolution": "Modern responsive single-page website with brand hero, service catalog, opening hours, and fast mobile contact triggers.",
                "risks": [
                    "Business owner may be comfortable with offline word-of-mouth",
                ],
            }

        # Intent 3: Website Generation
        if "generate" in lower_prompt and ("website" in lower_prompt or "prototype" in lower_prompt):
            return build_mock_website_copy(hints)

        # Intent 4: Pitch Generation
        if "pitch" in lower_prompt:
            demo_url = hints.get("demo_url", "http://localhost:5173/preview/demo")
            short_p = (
                f"Hello {business_name},\n\n"
                f"I came across your business while exploring {category.lower()} in {location}. "
                f"I noticed you don't have an active website for customers searching online on mobile.\n\n"
                f"I built a clean single-page prototype concept for {business_name} here:\n"
                f"{demo_url}\n\n"
                f"It can be fully tailored to your exact services and branding. If you'd like to see how it can help you get more inquiries, let's chat!"
            )
            email_p = (
                f"Subject: Website Concept & Digital Presence Proposal for {business_name}\n\n"
                f"Dear {business_name} Team,\n\n"
                f"I hope this message finds you well. While researching top-rated {category.lower()} in {location}, "
                f"I came across {business_name} and was impressed by your presence in the area.\n\n"
                f"I noticed that potential customers searching for your services online do not currently find an official website with your hours, service list, and quick contact options.\n\n"
                f"To help visualize what your modern digital presence could look like, I created a single-page prototype specifically tailored for {business_name}:\n\n"
                f"Interactive Prototype Demo: {demo_url}\n\n"
                f"This concept is mobile-responsive, lightning-fast, and includes click-to-call, service highlights, and your location map. It can be easily customized with your real photos, pricing, and exact offerings.\n\n"
                f"Would you be open to a brief 5-minute conversation this week to discuss customizing this for your business?\n\n"
                f"Warm regards,\n{self.settings.sender_name}"
            )
            detailed_p = (
                f"DIGITAL OPPORTUNITY & WEBSITE PROPOSAL\n"
                f"Prepared for: {business_name} ({location})\n"
                f"Prepared by: {self.settings.sender_name}\n\n"
                f"1. EXECUTIVE OVERVIEW\n"
                f"Modern consumers search for {category.lower()} services directly on smartphones. Currently, {business_name} lacks a dedicated web landing page, redirecting prospective high-intent customers to competing alternatives.\n\n"
                f"2. IDENTIFIED OPPORTUNITY\n"
                f"- Absence of a mobile-friendly showcase for {business_name}\n"
                f"- High friction for new customers seeking pricing, operating hours, and booking\n"
                f"- Significant opportunity to convert local search traffic into inbound inquiries\n\n"
                f"3. PROPOSED SOLUTION\n"
                f"A streamlined, high-speed single-page web portal designed for maximum local conversion.\n"
                f"Review Interactive Demo: {demo_url}\n\n"
                f"4. KEY FEATURES INCLUDED IN PROTOTYPE\n"
                f"- Hero introduction with clear brand identity\n"
                f"- Core services catalog\n"
                f"- Click-to-call & instant WhatsApp messaging\n"
                f"- Verified location & operating hours\n"
                f"- Zero maintenance overhead\n\n"
                f"5. NEXT STEPS\n"
                f"Review the prototype above. We can update this demo with your exact photography, menu/service list, and custom domain."
            )
            return {
                "short_pitch": short_p,
                "email_pitch": email_p,
                "detailed_pitch": detailed_p,
                "observations_referenced": [
                    "Missing official mobile landing page",
                    "Reliance on phone-only inquiries",
                    f"Strong local demand for {category.lower()} in {location}",
                ],
                "demo_link": demo_url,
            }

        # Fallback generic JSON
        return {
            "status": "success",
            "message": "Processed mock prompt",
            "business": business_name,
        }
