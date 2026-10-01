"""
Websites & Prototype Rendering Router.
Provides prototype JSON specifications and standalone HTML previews for iframe embedding.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Prototype, Lead
from app.schemas import PrototypeResponse

router = APIRouter(prefix="/websites", tags=["Websites & Prototypes"])


@router.get("/{lead_id}", response_model=PrototypeResponse)
async def get_prototype_json(lead_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve full structured prototype JSON for a lead."""
    stmt = select(Prototype).where(Prototype.lead_id == lead_id)
    proto = (await db.execute(stmt)).scalar_one_or_none()
    if not proto:
        raise HTTPException(status_code=404, detail="Website prototype not found for this lead")
    return proto


@router.get("/{lead_id}/render", response_class=HTMLResponse)
async def render_prototype_html(lead_id: str, db: AsyncSession = Depends(get_db)):
    """Render a standalone, fully-styled HTML single-page website prototype."""
    proto_stmt = select(Prototype).where(Prototype.lead_id == lead_id)
    proto_res = await db.execute(proto_stmt)
    proto = proto_res.scalar_one_or_none()

    lead_stmt = select(Lead).where(Lead.id == lead_id)
    lead = (await db.execute(lead_stmt)).scalar_one_or_none()

    if not proto or not lead:
        raise HTTPException(status_code=404, detail="Prototype or lead not found")

    cfg = proto.full_config or {}
    colors = proto.color_scheme or {"primary": "#2563EB", "secondary": "#0F172A", "background": "#F8FAFC", "surface": "#FFFFFF"}
    primary = colors.get("primary", "#2563EB")
    secondary = colors.get("secondary", "#0F172A")
    bg = colors.get("background", "#F8FAFC")
    surface = colors.get("surface", "#FFFFFF")

    hero = proto.hero_section or {}
    about = proto.about_section or {}
    services = proto.services_section.get("services", []) if proto.services_section else []
    why_us = proto.why_us_section.get("items", []) if proto.why_us_section else []
    gallery = proto.gallery_section.get("items", []) if proto.gallery_section else []
    contact = proto.contact_section or {}
    cta = proto.cta_section or {}

    # Build services cards HTML
    service_cards_html = "".join([
        f"""
        <div class="service-card">
            <div class="service-icon" style="background-color: {primary}15; color: {primary};">✦</div>
            <h3 style="color: {secondary};">{s.get('name', 'Service')}</h3>
            <p>{s.get('description', '')}</p>
        </div>
        """
        for s in services
    ])

    # Build why-us items HTML
    why_us_html = "".join([
        f"""
        <li class="why-item">
            <span style="color: {primary}; font-weight: bold; margin-right: 8px;">✓</span>
            <span>{item}</span>
        </li>
        """
        for item in why_us
    ])

    # Build gallery cards HTML
    gallery_html = "".join([
        f"""
        <div class="gallery-card">
            <div class="gallery-placeholder" style="background: linear-gradient(135deg, {secondary}20, {primary}30);">
                <span>{item.get('title', 'Featured Space')}</span>
            </div>
            <div class="gallery-meta">
                <strong>{item.get('title', 'Work')}</strong>
                <span class="gallery-tag">{item.get('category', 'Service')}</span>
            </div>
        </div>
        """
        for item in gallery
    ])

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{proto.site_title}</title>
    <meta name="description" content="{proto.tagline}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: {bg};
            color: #334155;
            line-height: 1.6;
        }}
        .proto-badge {{
            background: #1e1b4b;
            color: #c7d2fe;
            font-size: 12px;
            padding: 8px 16px;
            text-align: center;
            font-weight: 600;
            letter-spacing: 0.5px;
            border-bottom: 1px solid #3730a3;
        }}
        nav {{
            position: sticky;
            top: 0;
            background: rgba(255, 255, 255, 0.92);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid #e2e8f0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 18px 8%;
            z-index: 100;
        }}
        .brand-name {{
            font-size: 20px;
            font-weight: 800;
            color: {secondary};
        }}
        .nav-links a {{
            text-decoration: none;
            color: #475569;
            font-weight: 600;
            margin-left: 24px;
            font-size: 14px;
            transition: color 0.2s;
        }}
        .nav-links a:hover {{ color: {primary}; }}
        .btn {{
            display: inline-block;
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: 700;
            text-decoration: none;
            cursor: pointer;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }}
        .btn-primary {{
            background-color: {primary};
            color: #ffffff;
            box-shadow: 0 4px 14px {primary}40;
        }}
        .btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px {primary}60;
        }}
        .btn-secondary {{
            background-color: transparent;
            color: {secondary};
            border: 2px solid #cbd5e1;
            margin-left: 12px;
        }}
        .hero {{
            padding: 80px 8% 70px;
            text-align: center;
            max-width: 960px;
            margin: 0 auto;
        }}
        .hero-tag {{
            display: inline-block;
            background: {primary}15;
            color: {primary};
            font-weight: 700;
            font-size: 13px;
            padding: 6px 14px;
            border-radius: 9999px;
            margin-bottom: 20px;
        }}
        .hero h1 {{
            font-size: clamp(32px, 5vw, 54px);
            font-weight: 800;
            color: {secondary};
            line-height: 1.15;
            margin-bottom: 20px;
        }}
        .hero p {{
            font-size: 18px;
            color: #64748b;
            margin-bottom: 32px;
            max-width: 680px;
            margin-left: auto;
            margin-right: auto;
        }}
        section {{
            padding: 70px 8%;
        }}
        .section-header {{
            text-align: center;
            margin-bottom: 48px;
        }}
        .section-header h2 {{
            font-size: 32px;
            font-weight: 800;
            color: {secondary};
            margin-bottom: 12px;
        }}
        .section-header p {{
            font-size: 16px;
            color: #64748b;
        }}
        .services-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 24px;
        }}
        .service-card {{
            background: {surface};
            padding: 32px;
            border-radius: 14px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            transition: transform 0.2s;
        }}
        .service-card:hover {{
            transform: translateY(-4px);
            border-color: {primary}50;
        }}
        .service-icon {{
            width: 44px;
            height: 44px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            margin-bottom: 18px;
        }}
        .service-card h3 {{
            font-size: 20px;
            margin-bottom: 10px;
        }}
        .about-wrap {{
            background: {surface};
            border-radius: 16px;
            padding: 48px;
            border: 1px solid #e2e8f0;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 40px;
            align-items: center;
        }}
        .why-list {{
            list-style: none;
            margin-top: 20px;
        }}
        .why-item {{
            display: flex;
            align-items: flex-start;
            margin-bottom: 14px;
            font-size: 15px;
            color: #475569;
        }}
        .gallery-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 20px;
        }}
        .gallery-card {{
            background: {surface};
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid #e2e8f0;
        }}
        .gallery-placeholder {{
            height: 180px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            color: {secondary};
        }}
        .gallery-meta {{
            padding: 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .gallery-tag {{
            font-size: 12px;
            background: #f1f5f9;
            padding: 4px 10px;
            border-radius: 6px;
            color: #64748b;
        }}
        .contact-card {{
            background: {secondary};
            color: #ffffff;
            border-radius: 16px;
            padding: 48px;
            text-align: center;
        }}
        .contact-card h2 {{
            font-size: 32px;
            margin-bottom: 16px;
        }}
        .contact-info {{
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 28px;
            margin: 32px 0;
            font-size: 16px;
        }}
        .contact-info a {{
            color: #ffffff;
            text-decoration: underline;
        }}
        footer {{
            text-align: center;
            padding: 32px;
            font-size: 13px;
            color: #94a3b8;
            border-top: 1px solid #e2e8f0;
        }}
        @media (max-width: 768px) {{
            .about-wrap {{ grid-template-columns: 1fr; }}
            .nav-links {{ display: none; }}
        }}
    </style>
</head>
<body>
    <div class="proto-badge">
        ✦ INTERACTIVE CONCEPT PROTOTYPE — {lead.business_name} | Prepared for Proposal Review
    </div>

    <nav>
        <div class="brand-name">{lead.business_name}</div>
        <div class="nav-links">
            <a href="#about">About</a>
            <a href="#services">Services</a>
            <a href="#why-us">Why Us</a>
            <a href="#contact">Contact</a>
        </div>
        <div>
            <a href="tel:{contact.get('phone', '')}" class="btn btn-primary">{hero.get('primary_cta', 'Call Now')}</a>
        </div>
    </nav>

    <header class="hero">
        <div class="hero-tag">★ Premier {lead.category} in {lead.location}</div>
        <h1>{hero.get('headline', f'Welcome to {lead.business_name}')}</h1>
        <p>{hero.get('subheadline', '')}</p>
        <div>
            <a href="tel:{contact.get('phone', '')}" class="btn btn-primary">{hero.get('primary_cta', 'Contact Us')}</a>
            <a href="#services" class="btn btn-secondary">{hero.get('secondary_cta', 'Explore Services')}</a>
        </div>
    </header>

    <section id="services">
        <div class="section-header">
            <h2>{proto.services_section.get('title', 'Featured Services')}</h2>
            <p>{proto.services_section.get('subtitle', '')}</p>
        </div>
        <div class="services-grid">
            {service_cards_html}
        </div>
    </section>

    <section id="about">
        <div class="about-wrap">
            <div>
                <h2 style="color: {secondary}; font-size: 28px; margin-bottom: 16px;">{about.get('title', f'About {lead.business_name}')}</h2>
                <p style="margin-bottom: 20px;">{about.get('content', '')}</p>
                <div style="font-weight: 700; color: {secondary}; margin-bottom: 10px;">Our Commitments:</div>
                <ul class="why-list">
                    { "".join([f'<li class="why-item"><span style="color: {primary}; font-weight: bold; margin-right: 8px;">✦</span><span>{h}</span></li>' for h in about.get('highlights', [])]) }
                </ul>
            </div>
            <div id="why-us">
                <h3 style="color: {secondary}; font-size: 22px; margin-bottom: 14px;">Why Clients Trust Us</h3>
                <ul class="why-list">
                    {why_us_html}
                </ul>
            </div>
        </div>
    </section>

    <section id="gallery">
        <div class="section-header">
            <h2>{proto.gallery_section.get('title', 'Gallery & Atmosphere')}</h2>
            <p>A glimpse into our location, standards, and dedicated space</p>
        </div>
        <div class="gallery-grid">
            {gallery_html}
        </div>
    </section>

    <section id="contact">
        <div class="contact-card">
            <h2>{cta.get('heading', 'Ready to Connect?')}</h2>
            <p>{cta.get('subheading', f'Visit us at {lead.location} or give us a call today.')}</p>
            <div class="contact-info">
                <div>📍 <strong>Address:</strong> {contact.get('address', lead.location)}</div>
                <div>📞 <strong>Phone:</strong> <a href="tel:{contact.get('phone', '')}">{contact.get('phone', 'Available on request')}</a></div>
                <div>⏰ <strong>Hours:</strong> {contact.get('hours', 'Mon - Sat: 9am - 6pm')}</div>
            </div>
            <div>
                <a href="tel:{contact.get('phone', '')}" class="btn btn-primary" style="background: #ffffff; color: {secondary};">{cta.get('button_text', 'Call Now')}</a>
            </div>
        </div>
    </section>

    <footer>
        <p>© 2026 {lead.business_name}. Prototype proposal designed for digital optimization.</p>
        <p style="margin-top: 6px; font-size: 11px;">Note: This demo page was created as an evaluation prototype by {cfg.get('disclaimer', 'Web Architecture Team')}.</p>
    </footer>
</body>
</html>
"""
    return HTMLResponse(content=html_content)
