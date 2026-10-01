"""
Varied mock website copy for demo / mock-LLM mode.
Produces category-aware, per-business copy so prototypes don't all read the same
when no real LLM is configured. Selection is deterministic per seed.
"""

import hashlib
from typing import Dict, Any, List
from app.services.design_themes import get_category_group, short_business_name


# Category-specific offerings: (name, description, icon)
GROUP_OFFERINGS: Dict[str, List[tuple]] = {
    "food": [
        ("Signature House Specials", "Our most-loved dishes, prepared fresh to order every day.", "ChefHat"),
        ("Freshly Brewed Beverages", "Hot and cold drinks, from strong coffee to refreshing chillers.", "Coffee"),
        ("Breakfast & Brunch", "Hearty morning plates to start your day right.", "Sun"),
        ("Snacks & Quick Bites", "Light bites perfect for a short break or an evening hangout.", "Sandwich"),
        ("Desserts & Sweets", "Sweet treats to finish your meal on a high note.", "Cake"),
        ("Takeaway & Delivery", "Order ahead and enjoy your favourites at home or the office.", "Bike"),
        ("Family & Group Orders", "Platters and combos sized for families and get-togethers.", "Users"),
        ("Party & Event Catering", "Menus for birthdays, office events and celebrations.", "PartyPopper"),
    ],
    "beauty": [
        ("Haircuts & Styling", "Precision cuts and styling for every look.", "Scissors"),
        ("Hair Colour & Treatments", "Colour, smoothening and nourishing hair therapies.", "Palette"),
        ("Skin Care & Facials", "Cleansing and glow facials tailored to your skin type.", "Sparkles"),
        ("Bridal & Party Makeup", "Event-ready looks for your special occasions.", "Heart"),
        ("Manicure & Pedicure", "Relaxing nail care and polish services.", "Hand"),
        ("Grooming Packages", "Bundled services for a complete refresh.", "Gift"),
    ],
    "fitness": [
        ("Strength Training", "Structured programs to build strength safely.", "Dumbbell"),
        ("Personal Coaching", "One-on-one sessions focused on your goals.", "User"),
        ("Group Classes", "High-energy group workouts for all levels.", "Users"),
        ("Cardio & Conditioning", "Improve stamina with guided cardio routines.", "Activity"),
        ("Nutrition Guidance", "Practical diet advice to support your training.", "Apple"),
        ("Flexible Memberships", "Monthly and quarterly plans to suit your schedule.", "CalendarCheck"),
    ],
    "health": [
        ("General Consultations", "Walk-in and scheduled consultations.", "Stethoscope"),
        ("Preventive Check-ups", "Routine screening to keep you ahead of issues.", "HeartPulse"),
        ("Specialised Treatments", "Focused care for specific conditions.", "Shield"),
        ("Follow-up Care", "Ongoing support and progress reviews.", "ClipboardCheck"),
        ("Appointment Booking", "Easy scheduling by phone or message.", "Calendar"),
    ],
    "auto": [
        ("General Servicing", "Routine maintenance to keep your vehicle running smoothly.", "Wrench"),
        ("Diagnostics & Repairs", "Accurate fault finding and dependable repairs.", "Gauge"),
        ("Tyres & Wheel Care", "Replacement, alignment and balancing.", "Disc"),
        ("Washing & Detailing", "Interior and exterior cleaning for a fresh finish.", "Droplets"),
        ("Pickup & Drop", "Convenient vehicle pickup for busy schedules.", "Truck"),
    ],
    "retail": [
        ("New Arrivals", "Fresh stock added regularly.", "Tag"),
        ("Best Sellers", "Customer favourites always in stock.", "Star"),
        ("Gifting Options", "Thoughtful picks for every occasion.", "Gift"),
        ("Order on Call / WhatsApp", "Reserve items before you visit.", "Phone"),
        ("Easy Exchanges", "Hassle-free exchange support.", "RefreshCw"),
    ],
    "default": [
        ("Core Services", "Professional service tailored to your requirements.", "Briefcase"),
        ("Consultation & Guidance", "Advice to help you pick the right option.", "MessageSquare"),
        ("Priority Support", "Prompt scheduling and responsive follow-up.", "ShieldCheck"),
        ("Custom Packages", "Flexible packages designed around your needs.", "Package"),
    ],
}

GROUP_SERVICE_TITLES: Dict[str, List[str]] = {
    "food": ["Our Menu Highlights", "What's Cooking", "Taste Our Favourites", "From Our Kitchen"],
    "beauty": ["Our Treatments", "Services & Rituals", "Look & Feel Your Best"],
    "fitness": ["Programs & Training", "How We Train", "Choose Your Program"],
    "health": ["Our Care Services", "How We Can Help", "Treatments & Consultations"],
    "auto": ["Workshop Services", "What We Fix", "Vehicle Care Services"],
    "retail": ["Shop With Us", "What We Offer", "Browse Our Range"],
    "default": ["Our Services", "What We Do", "How We Can Help"],
}

GROUP_GALLERY: Dict[str, List[tuple]] = {
    "food": [("Our Dining Space", "Ambience"), ("Fresh From the Kitchen", "Food"), ("Chef's Specials", "Menu"),
             ("Evening Vibes", "Ambience"), ("Takeaway Counter", "Service")],
    "beauty": [("Styling Stations", "Salon"), ("Relaxation Area", "Ambience"), ("Before & After", "Results")],
    "fitness": [("Training Floor", "Facility"), ("Group Sessions", "Classes"), ("Equipment Zone", "Facility")],
    "health": [("Reception & Waiting", "Facility"), ("Consultation Room", "Care"), ("Modern Equipment", "Facility")],
    "auto": [("Service Bay", "Workshop"), ("Diagnostic Tools", "Equipment"), ("Ready for Delivery", "Results")],
    "retail": [("Store Front", "Shop"), ("Product Displays", "Range"), ("Billing Counter", "Service")],
    "default": [("Our Space", "Premises"), ("At Work", "Service"), ("Welcoming Team", "People")],
}

HEADLINES = [
    "Welcome to {name}",
    "{name} — {location}'s Favourite {category}",
    "Discover {name}",
    "Experience {name}, Right Here in {location}",
    "Your Go-To {category} in {location}",
]

SUBHEADLINES = {
    "food": [
        "Fresh flavours, warm hospitality and a place you'll want to come back to.",
        "Great food, friendly service and a cosy spot to unwind in {location}.",
        "Made fresh every day for food lovers across {location}.",
    ],
    "default": [
        "Dependable {category_lower} for customers across {location}.",
        "Friendly, professional {category_lower} you can rely on in {location}.",
        "Serving the {location} community with care and attention to detail.",
    ],
}

PRIMARY_CTAS = {
    "food": ["View Menu", "Order Now", "Reserve a Table", "Call to Order"],
    "beauty": ["Book Appointment", "Call to Book", "Reserve a Slot"],
    "fitness": ["Join Now", "Book a Free Trial", "Start Training"],
    "health": ["Book Appointment", "Call the Clinic", "Schedule a Visit"],
    "default": ["Contact Us", "Call Now", "Get a Quote", "Enquire Now"],
}

HOURS = {
    "food": ["Daily: 8:00 AM - 11:00 PM", "Mon - Sun: 10:00 AM - 10:30 PM", "Daily: 7:30 AM - 10:00 PM"],
    "default": ["Mon - Sat: 9:00 AM - 7:00 PM | Sun: Closed", "Mon - Sat: 10:00 AM - 8:00 PM", "Daily: 9:00 AM - 9:00 PM"],
}

WHY_US = [
    "Locally run with personal attention for every customer",
    "Conveniently located in {location}",
    "Honest pricing with no hidden charges",
    "Consistent quality you can count on",
    "Quick response on calls and WhatsApp",
    "Clean, comfortable and welcoming space",
]


def _rng_bytes(seed: str) -> bytes:
    return hashlib.sha256(("copy:" + (seed or "")).encode("utf-8")).digest()


def _choose(options: List[Any], b: bytes, i: int) -> Any:
    return options[b[i % len(b)] % len(options)]


def _sample(options: List[Any], b: bytes, start: int, k: int) -> List[Any]:
    """Deterministic sample of k distinct items."""
    pool = list(options)
    picked = []
    for j in range(min(k, len(pool))):
        picked.append(pool.pop(b[(start + j) % len(b)] % len(pool)))
    return picked


def build_mock_website_copy(hints: Dict[str, Any]) -> Dict[str, Any]:
    """Build varied, category-aware prototype copy for one business."""
    name = short_business_name(hints.get("business_name", "Local Business"))
    category = hints.get("category", "General Services")
    location = hints.get("location", "Local Area")
    phone = hints.get("phone") or "Available on request"
    seed = hints.get("variant_seed") or name
    group = get_category_group(category)
    b = _rng_bytes(seed)
    # Rotation slot keeps headline/section titles distinct between consecutive leads
    idx = hints.get("variant_index")
    rot = (lambda opts, i: opts[idx % len(opts)]) if idx is not None else (lambda opts, i: _choose(opts, b, i))
    fmt = {"name": name, "location": location, "category": category, "category_lower": category.lower()}

    offerings = _sample(GROUP_OFFERINGS.get(group, GROUP_OFFERINGS["default"]), b, 0, 3 + b[10] % 2)
    gallery = _sample(GROUP_GALLERY.get(group, GROUP_GALLERY["default"]), b, 12, 3)
    why_us = _sample(WHY_US, b, 16, 3)

    return {
        "site_title": f"{name} | {category} in {location}",
        "tagline": _choose([
            f"{category} in {location}, done right",
            f"Proudly serving {location}",
            f"Where {location} comes for {category.lower()}",
        ], b, 20),
        "hero_section": {
            "headline": rot(HEADLINES, 21).format(**fmt),
            "subheadline": _choose(SUBHEADLINES.get(group, SUBHEADLINES["default"]), b, 22).format(**fmt),
            "primary_cta": rot(PRIMARY_CTAS.get(group, PRIMARY_CTAS["default"]), 23),
            "secondary_cta": _choose(["Explore More", "See What We Offer", "Find Us"], b, 24),
        },
        "about_section": {
            "title": _choose([f"About {name}", "Our Story", f"Why {location} Loves {name}"], b, 25),
            "content": _choose([
                f"{name} is a local {category.lower()} in {location}, focused on quality and a warm, welcoming experience.",
                f"At {name}, we keep things simple: good service, fair prices and customers who feel at home.",
                f"From regulars to first-time visitors, {name} has been part of everyday life in {location}.",
            ], b, 26),
            "highlights": [h.format(**fmt) for h in _sample(WHY_US, b, 27, 3)],
        },
        "services_section": {
            "title": rot(GROUP_SERVICE_TITLES.get(group, GROUP_SERVICE_TITLES["default"]), 28),
            "subtitle": f"A taste of what {name} has to offer",
            "services": [{"name": n, "description": d, "icon": i} for n, d, i in offerings],
        },
        "why_us_section": {
            "title": f"Why Choose {name}",
            "items": [w.format(**fmt) for w in why_us],
        },
        "gallery_section": {
            "title": _choose(["A Look Inside", "Gallery", f"Moments at {name}"], b, 29),
            "items": [{"title": t, "category": c} for t, c in gallery],
        },
        "contact_section": {
            "title": _choose(["Visit Us", "Get in Touch", "Find Us"], b, 30),
            "address": location,
            "phone": phone,
            "email": hints.get("email") or "",
            "hours": _choose(HOURS.get(group, HOURS["default"]), b, 31),
        },
        "cta_section": {
            "heading": _choose([
                f"Come Visit {name} Today",
                "Ready When You Are",
                f"See You Soon at {name}",
            ], b, 1),
            "subheading": f"Call us or drop by our place in {location}.",
            "button_text": _choose(["Call Now", "Get Directions", "Contact Us"], b, 2),
        },
    }
