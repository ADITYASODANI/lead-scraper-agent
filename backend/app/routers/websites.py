"""
Websites & Prototype Rendering Router.
Provides prototype JSON specifications and standalone HTML previews for iframe embedding.
"""

import html
from urllib.parse import quote_plus
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Prototype, Lead
from app.schemas import PrototypeResponse
from app.services.design_themes import pick_design, short_business_name

router = APIRouter(prefix="/websites", tags=["Websites & Prototypes"])


@router.get("/{lead_id}", response_model=PrototypeResponse)
async def get_prototype_json(lead_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve full structured prototype JSON for a lead."""
    stmt = select(Prototype).where(Prototype.lead_id == lead_id)
    proto = (await db.execute(stmt)).scalar_one_or_none()
    if not proto:
        raise HTTPException(status_code=404, detail="Website prototype not found for this lead")
    return proto


GROUP_ICONS = {
    "food": ["🍽️", "☕", "🥘", "🍰", "🥤", "🍕", "🧁", "🍜"],
    "beauty": ["✂️", "💅", "💄", "🌸", "✨", "💆"],
    "fitness": ["🏋️", "🔥", "🏃", "🥗", "💪", "⏱️"],
    "health": ["🩺", "❤️", "🛡️", "📋", "📅"],
    "auto": ["🔧", "⚙️", "🛞", "🚿", "🚚"],
    "retail": ["🏷️", "⭐", "🎁", "📞", "🔄"],
    "default": ["✦", "💬", "🛡️", "📦"],
}


def _e(value) -> str:
    """HTML-escape scraped / generated text before inserting into the page."""
    return html.escape(str(value or ""), quote=True)


@router.get("/{lead_id}/render", response_class=HTMLResponse)
async def render_prototype_html(lead_id: str, db: AsyncSession = Depends(get_db)):
    """Render a standalone, fully-styled HTML single-page website prototype."""
    proto_stmt = select(Prototype).where(Prototype.lead_id == lead_id)
    proto = (await db.execute(proto_stmt)).scalar_one_or_none()

    lead_stmt = select(Lead).where(Lead.id == lead_id)
    lead = (await db.execute(lead_stmt)).scalar_one_or_none()

    if not proto or not lead:
        raise HTTPException(status_code=404, detail="Prototype or lead not found")

    cfg = proto.full_config or {}
    # Older prototypes have no stored design: derive one from the lead id
    design = cfg.get("design") or pick_design(lead.id, lead.category)
    colors = design.get("palette") or proto.color_scheme or {}
    primary = colors.get("primary", "#2563EB")
    secondary = colors.get("secondary", "#0F172A")
    accent = colors.get("accent", primary)
    bg = colors.get("background", "#F8FAFC")
    surface = colors.get("surface", "#FFFFFF")

    fonts = design.get("fonts", {"heading": "Plus Jakarta Sans", "body": "Plus Jakarta Sans"})
    heading_font, body_font = fonts["heading"], fonts["body"]
    font_families = "&".join(
        f"family={quote_plus(f)}:wght@400;600;700;800" for f in dict.fromkeys([heading_font, body_font])
    )
    hero_style = design.get("hero_style", "centered")
    card_style = design.get("card_style", "bordered")
    radius = design.get("radius", 12)
    btn_radius = design.get("button_radius", 10)
    section_order = design.get("section_order", ["services", "about", "gallery", "map", "contact"])
    icons = GROUP_ICONS.get(design.get("group", "default"), GROUP_ICONS["default"])

    hero = proto.hero_section or {}
    about = proto.about_section or {}
    services_sec = proto.services_section or {}
    services = services_sec.get("services", [])
    why_us = (proto.why_us_section or {}).get("items", [])
    gallery_sec = proto.gallery_section or {}
    gallery = gallery_sec.get("items", [])
    contact = proto.contact_section or {}
    cta = proto.cta_section or {}

    name = _e(short_business_name(lead.business_name))
    category = _e(lead.category)
    location = _e(lead.location)
    phone = contact.get("phone") or lead.phone or ""
    tel = _e("".join(ch for ch in phone if ch.isdigit() or ch == "+"))
    map_query = quote_plus(f"{lead.business_name} {lead.location}")
    maps_link = next(
        (u for u in (lead.source_urls or []) if "/maps/place/" in u),
        f"https://www.google.com/maps/search/?api=1&query={map_query}",
    )

    card_css = {
        "bordered": f"border: 1px solid #e2e8f0; box-shadow: none; background: {surface};",
        "shadow": f"border: none; box-shadow: 0 12px 30px -12px rgba(15,23,42,0.25); background: {surface};",
        "filled": f"border: none; box-shadow: none; background: {primary}12;",
    }.get(card_style, "")

    service_cards_html = "".join(
        f"""
        <div class="card service-card">
            <div class="service-icon">{icons[i % len(icons)]}</div>
            <h3>{_e(s.get('name', 'Service'))}</h3>
            <p>{_e(s.get('description', ''))}</p>
        </div>"""
        for i, s in enumerate(services)
    )
    why_us_html = "".join(f'<li class="why-item"><span class="tick">✓</span><span>{_e(item)}</span></li>' for item in why_us)
    highlights_html = "".join(f'<li class="why-item"><span class="tick">✦</span><span>{_e(h)}</span></li>' for h in about.get("highlights", []))
    gallery_html = "".join(
        f"""
        <div class="card gallery-card">
            <div class="gallery-placeholder" style="background: linear-gradient({(i * 67 + 120) % 360}deg, {primary}{'55' if i % 2 else '33'}, {accent}44, {secondary}22);">
                <span class="g-icon">{icons[(i + 2) % len(icons)]}</span>
            </div>
            <div class="gallery-meta">
                <strong>{_e(item.get('title', 'Featured'))}</strong>
                <span class="gallery-tag">{_e(item.get('category', ''))}</span>
            </div>
        </div>"""
        for i, item in enumerate(gallery)
    )

    initials = "".join(w[0] for w in short_business_name(lead.business_name).split()[:2]).upper() or "★"
    primary_btn = f'<a href="tel:{tel}" class="btn btn-primary">{_e(hero.get("primary_cta", "Contact Us"))}</a>'
    secondary_btn = f'<a href="#services" class="btn btn-secondary">{_e(hero.get("secondary_cta", "Explore"))}</a>'
    hero_text = f"""
            <div class="hero-tag">★ {category} in {location}</div>
            <h1>{_e(hero.get('headline') or f'Welcome to {short_business_name(lead.business_name)}')}</h1>
            <p class="hero-sub">{_e(hero.get('subheadline', ''))}</p>
            <div class="hero-actions">{primary_btn}{secondary_btn}</div>"""

    if hero_style == "split":
        hero_html = f"""
    <header class="hero hero-split">
        <div class="hero-copy">{hero_text}</div>
        <div class="hero-visual">
            <div class="monogram">{_e(initials)}</div>
            <div class="visual-info">
                <div>📍 {location}</div>
                <div>⏰ {_e(contact.get('hours', ''))}</div>
                {f'<div>📞 {_e(phone)}</div>' if phone else ''}
            </div>
        </div>
    </header>"""
    else:
        hero_html = f'<header class="hero hero-{hero_style}" data-mono="{_e(initials)}"><div class="hero-inner">{hero_text}</div></header>'

    hero_css = {
        "centered": f".hero {{ padding: 90px 8% 80px; text-align: center; }} .hero-inner {{ max-width: 860px; margin: 0 auto; }} .hero-sub {{ margin-left: auto; margin-right: auto; }}",
        "split": f".hero-split {{ display: grid; grid-template-columns: 1.2fr 1fr; gap: 48px; align-items: center; padding: 80px 8%; }}"
                 f" .hero-visual {{ background: linear-gradient(145deg, {primary}, {secondary}); color: #fff; border-radius: {radius * 2}px; padding: 40px; min-height: 340px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 30px 60px -20px {primary}80; }}"
                 f" .monogram {{ font-family: '{heading_font}', serif; font-size: 96px; font-weight: 800; line-height: 1; opacity: .95; }}"
                 f" .visual-info div {{ margin-top: 10px; font-size: 15px; opacity: .92; }}",
        "dark": f".hero-dark {{ background: radial-gradient(circle at 80% 20%, {primary}66, transparent 55%), {secondary}; color: #fff; padding: 110px 8% 100px; }}"
                f" .hero-dark .hero-inner {{ max-width: 760px; }} .hero-dark h1 {{ color: #fff !important; }} .hero-dark .hero-sub {{ color: #e2e8f0 !important; }}"
                f" .hero-dark .hero-tag {{ background: rgba(255,255,255,.12) !important; color: #fff !important; }} .hero-dark .btn-secondary {{ color: #fff !important; border-color: rgba(255,255,255,.4) !important; }}",
        "left": f".hero-left {{ padding: 90px 8% 80px; background: linear-gradient(180deg, {primary}10, transparent); }}"
                f" .hero-left .hero-inner {{ max-width: 720px; border-left: 6px solid {accent}; padding-left: 32px; position: relative; z-index: 1; }}"
                f" .hero-left {{ position: relative; overflow: hidden; }}"
                f" .hero-left::after {{ content: attr(data-mono); position: absolute; right: 6%; top: 50%; transform: translateY(-50%); font-family: '{heading_font}', serif; font-size: clamp(120px, 22vw, 320px); font-weight: 800; color: {primary}; opacity: .09; line-height: 1; }}",
    }.get(hero_style, "")

    sections = {
        "services": f"""
    <section id="services">
        <div class="section-header">
            <h2>{_e(services_sec.get('title', 'Our Services'))}</h2>
            <p>{_e(services_sec.get('subtitle', ''))}</p>
        </div>
        <div class="services-grid">{service_cards_html}</div>
    </section>""",
        "about": f"""
    <section id="about">
        <div class="card about-wrap">
            <div>
                <h2 class="h2">{_e(about.get('title', f'About {lead.business_name}'))}</h2>
                <p style="margin-bottom: 20px;">{_e(about.get('content', ''))}</p>
                <ul class="why-list">{highlights_html}</ul>
            </div>
            <div id="why-us">
                <h3 class="h3">{_e((proto.why_us_section or {}).get('title', 'Why Choose Us'))}</h3>
                <ul class="why-list">{why_us_html}</ul>
            </div>
        </div>
    </section>""",
        "gallery": f"""
    <section id="gallery">
        <div class="section-header">
            <h2>{_e(gallery_sec.get('title', 'Gallery'))}</h2>
            <p>Real photos of {name} can be placed here</p>
        </div>
        <div class="gallery-grid">{gallery_html}</div>
    </section>""",
        "map": f"""
    <section id="map">
        <div class="section-header">
            <h2>Find {name}</h2>
            <p>{location}</p>
        </div>
        <div class="map-wrap">
            <iframe title="Map" loading="lazy" src="https://maps.google.com/maps?q={map_query}&output=embed"></iframe>
        </div>
        <p style="text-align:center; margin-top:16px;"><a class="map-link" href="{_e(maps_link)}" target="_blank" rel="noopener">Open in Google Maps ↗</a></p>
    </section>""",
        "contact": f"""
    <section id="contact">
        <div class="contact-card">
            <h2>{_e(cta.get('heading', 'Ready to Connect?'))}</h2>
            <p>{_e(cta.get('subheading', ''))}</p>
            <div class="contact-info">
                <div>📍 <strong>Address:</strong> {_e(contact.get('address', lead.location))}</div>
                {f'<div>📞 <strong>Phone:</strong> <a href="tel:{tel}">{_e(phone)}</a></div>' if phone else ''}
                <div>⏰ <strong>Hours:</strong> {_e(contact.get('hours', ''))}</div>
                {f'<div>✉️ <strong>Email:</strong> {_e(contact.get("email"))}</div>' if contact.get('email') else ''}
            </div>
            <a href="tel:{tel}" class="btn" style="background: #ffffff; color: {secondary};">{_e(cta.get('button_text', 'Call Now'))}</a>
        </div>
    </section>""",
    }
    body_sections = "".join(sections[k] for k in section_order if k in sections)
    nav_dark = hero_style == "dark"

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{_e(proto.site_title)}</title>
    <meta name="description" content="{_e(proto.tagline)}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?{font_families}&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html {{ scroll-behavior: smooth; }}
        body {{ font-family: '{body_font}', -apple-system, BlinkMacSystemFont, sans-serif; background: {bg}; color: #334155; line-height: 1.65; }}
        h1, h2, h3, .brand-name, .h2, .h3 {{ font-family: '{heading_font}', serif; color: {secondary}; }}
        .proto-badge {{ background: #1e1b4b; color: #c7d2fe; font-size: 12px; padding: 8px 16px; text-align: center; font-weight: 600; letter-spacing: .5px; }}
        nav {{ gap: 20px; position: sticky; top: 0; z-index: 100; display: flex; justify-content: space-between; align-items: center; padding: 18px 8%;
               background: {'%s' % secondary if nav_dark else 'rgba(255,255,255,.92)'}; backdrop-filter: blur(12px);
               border-bottom: 1px solid {'rgba(255,255,255,.08)' if nav_dark else '#e2e8f0'}; }}
        .brand-name {{ font-size: 21px; font-weight: 800; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 40%; {'color: #fff;' if nav_dark else ''} }}
        .nav-links {{ white-space: nowrap; }} .nav-links a {{ text-decoration: none; color: {'#cbd5e1' if nav_dark else '#475569'}; font-weight: 600; margin-left: 24px; font-size: 14px; }}
        .nav-links a:hover {{ color: {accent}; }}
        .btn {{ white-space: nowrap; display: inline-block; padding: 12px 26px; border-radius: {btn_radius}px; font-weight: 700; text-decoration: none; transition: transform .15s ease, box-shadow .15s ease; }}
        .btn:hover {{ transform: translateY(-2px); }}
        .btn-primary {{ background: {primary}; color: #fff; box-shadow: 0 6px 18px {primary}40; }}
        .btn-secondary {{ background: transparent; color: {secondary}; border: 2px solid #cbd5e1; margin-left: 12px; }}
        .hero-tag {{ display: inline-block; background: {primary}18; color: {primary}; font-weight: 700; font-size: 13px; padding: 6px 14px; border-radius: 9999px; margin-bottom: 20px; }}
        .hero h1 {{ font-size: clamp(34px, 5vw, 58px); font-weight: 800; line-height: 1.12; margin-bottom: 20px; }}
        .hero-sub {{ font-size: 18px; color: #64748b; margin-bottom: 32px; max-width: 640px; }}
        {hero_css}
        section {{ padding: 72px 8%; }}
        .section-header {{ text-align: center; margin-bottom: 44px; }}
        .section-header h2 {{ font-size: 34px; font-weight: 800; margin-bottom: 10px; }}
        .section-header p {{ color: #64748b; }}
        .card {{ border-radius: {radius}px; {card_css} }}
        .services-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 24px; }}
        .service-card {{ padding: 30px; transition: transform .2s; }}
        .service-card:hover {{ transform: translateY(-4px); }}
        .service-icon {{ width: 50px; height: 50px; border-radius: {max(radius - 2, 4)}px; display: flex; align-items: center; justify-content: center; font-size: 24px; margin-bottom: 18px; background: {primary}15; }}
        .service-card h3 {{ font-size: 19px; margin-bottom: 8px; }}
        .about-wrap {{ padding: 48px; display: grid; grid-template-columns: 1fr 1fr; gap: 40px; }}
        .h2 {{ font-size: 28px; margin-bottom: 16px; }} .h3 {{ font-size: 22px; margin-bottom: 14px; }}
        .why-list {{ list-style: none; }}
        .why-item {{ display: flex; margin-bottom: 12px; color: #475569; }}
        .tick {{ color: {primary}; font-weight: bold; margin-right: 10px; }}
        .gallery-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 20px; }}
        .gallery-card {{ overflow: hidden; }}
        .gallery-placeholder {{ height: 190px; display: flex; align-items: center; justify-content: center; }}
        .g-icon {{ font-size: 54px; filter: drop-shadow(0 6px 10px rgba(0,0,0,.15)); }}
        .gallery-meta {{ padding: 16px; display: flex; justify-content: space-between; align-items: center; gap: 8px; }}
        .gallery-tag {{ font-size: 12px; background: {accent}22; padding: 4px 10px; border-radius: 6px; color: {secondary}; }}
        .map-wrap {{ border-radius: {radius}px; overflow: hidden; border: 1px solid #e2e8f0; height: 360px; }}
        .map-wrap iframe {{ width: 100%; height: 100%; border: 0; }}
        .map-link {{ color: {primary}; font-weight: 700; text-decoration: none; }}
        .contact-card {{ background: linear-gradient(135deg, {secondary}, {primary}); color: #fff; border-radius: {radius + 4}px; padding: 52px; text-align: center; }}
        .contact-card h2 {{ color: #fff; font-size: 32px; margin-bottom: 12px; }}
        .contact-info {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 24px; margin: 30px 0; }}
        .contact-info a {{ color: #fff; }}
        footer {{ text-align: center; padding: 32px; font-size: 13px; color: #94a3b8; border-top: 1px solid #e2e8f0; }}
        @media (max-width: 820px) {{
            .about-wrap, .hero-split {{ grid-template-columns: 1fr; }}
            .nav-links {{ display: none; }}
            .about-wrap, .contact-card {{ padding: 28px; }}
            .btn-secondary {{ margin-left: 0; margin-top: 10px; }}
        }}
    </style>
</head>
<body>
    <div class="proto-badge">✦ CONCEPT PROTOTYPE — {name} | Theme: {_e(design.get('theme_name', 'Custom'))}</div>
    <nav>
        <div class="brand-name">{name}</div>
        <div class="nav-links">
            <a href="#services">{'Menu' if design.get('group') == 'food' else 'Services'}</a>
            <a href="#about">About</a>
            <a href="#gallery">Gallery</a>
            <a href="#map">Location</a>
            <a href="#contact">Contact</a>
        </div>
        {primary_btn}
    </nav>
    {hero_html}
    {body_sections}
    <footer>
        <p>© 2026 {name}. Prototype proposal designed for digital optimization.</p>
        <p style="margin-top: 6px; font-size: 11px;">{_e(cfg.get('disclaimer', 'AI-generated prototype concept for evaluation purposes.'))}</p>
    </footer>
</body>
</html>
"""
    return HTMLResponse(content=html_content)
