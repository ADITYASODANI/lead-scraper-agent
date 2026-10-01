"""
Design Theme Selector for website prototypes.
Deterministically picks a distinct visual design (palette, typography, layout)
per lead so every generated prototype looks different, while staying stable
across re-renders of the same lead.
"""

import hashlib
from typing import Dict, Any, List, Optional


# Category groups -> keywords that map a free-text category onto a group
CATEGORY_GROUPS: Dict[str, List[str]] = {
    "food": ["cafe", "coffee", "restaurant", "food", "bakery", "dhaba", "paratha", "partha",
             "pizza", "bar", "bistro", "kitchen", "sweet", "tea", "juice", "dessert", "eatery"],
    "beauty": ["salon", "spa", "beauty", "barber", "parlour", "parlor", "nail", "makeup"],
    "fitness": ["gym", "fitness", "yoga", "crossfit", "studio", "martial", "dance"],
    "health": ["clinic", "dental", "dentist", "doctor", "hospital", "physio", "pharmacy", "health"],
    "auto": ["car", "auto", "garage", "mechanic", "bike", "tyre", "tire", "motor"],
    "retail": ["retail", "store", "shop", "boutique", "mart", "jewel", "fashion", "electronics"],
}

# Several harmonious palettes per group; one is chosen per lead
GROUP_PALETTES: Dict[str, List[Dict[str, str]]] = {
    "food": [
        {"name": "Espresso", "primary": "#78350F", "secondary": "#1C1917", "accent": "#D97706", "background": "#FDF8F3", "surface": "#FFFFFF"},
        {"name": "Saffron", "primary": "#EA580C", "secondary": "#431407", "accent": "#FACC15", "background": "#FFFBEB", "surface": "#FFFFFF"},
        {"name": "Olive Garden", "primary": "#4D7C0F", "secondary": "#1A2E05", "accent": "#CA8A04", "background": "#F7FEE7", "surface": "#FFFFFF"},
        {"name": "Masala", "primary": "#B91C1C", "secondary": "#2A0A0A", "accent": "#F59E0B", "background": "#FEF2F2", "surface": "#FFFFFF"},
        {"name": "Mint Cafe", "primary": "#0F766E", "secondary": "#042F2E", "accent": "#F97316", "background": "#F0FDFA", "surface": "#FFFFFF"},
    ],
    "beauty": [
        {"name": "Rose", "primary": "#DB2777", "secondary": "#18181B", "accent": "#F43F5E", "background": "#FDF2F8", "surface": "#FFFFFF"},
        {"name": "Lavender", "primary": "#7C3AED", "secondary": "#1E1B4B", "accent": "#C084FC", "background": "#FAF5FF", "surface": "#FFFFFF"},
        {"name": "Champagne", "primary": "#A16207", "secondary": "#1C1917", "accent": "#E879F9", "background": "#FEFCE8", "surface": "#FFFFFF"},
    ],
    "fitness": [
        {"name": "Power Red", "primary": "#DC2626", "secondary": "#09090B", "accent": "#F97316", "background": "#FAFAFA", "surface": "#FFFFFF"},
        {"name": "Volt", "primary": "#65A30D", "secondary": "#0A0A0A", "accent": "#FACC15", "background": "#F7FEE7", "surface": "#FFFFFF"},
        {"name": "Electric", "primary": "#2563EB", "secondary": "#020617", "accent": "#06B6D4", "background": "#F8FAFC", "surface": "#FFFFFF"},
    ],
    "health": [
        {"name": "Clinical Blue", "primary": "#0284C7", "secondary": "#0F172A", "accent": "#0EA5E9", "background": "#F0F9FF", "surface": "#FFFFFF"},
        {"name": "Teal Care", "primary": "#0D9488", "secondary": "#134E4A", "accent": "#14B8A6", "background": "#F0FDFA", "surface": "#FFFFFF"},
        {"name": "Calm Indigo", "primary": "#4F46E5", "secondary": "#1E1B4B", "accent": "#22C55E", "background": "#EEF2FF", "surface": "#FFFFFF"},
    ],
    "auto": [
        {"name": "Garage Blue", "primary": "#2563EB", "secondary": "#1E293B", "accent": "#F59E0B", "background": "#F8FAFC", "surface": "#FFFFFF"},
        {"name": "Racing", "primary": "#E11D48", "secondary": "#111827", "accent": "#FBBF24", "background": "#F9FAFB", "surface": "#FFFFFF"},
        {"name": "Steel", "primary": "#475569", "secondary": "#0F172A", "accent": "#F97316", "background": "#F1F5F9", "surface": "#FFFFFF"},
    ],
    "retail": [
        {"name": "Indigo Shop", "primary": "#4F46E5", "secondary": "#18181B", "accent": "#6366F1", "background": "#F5F3FF", "surface": "#FFFFFF"},
        {"name": "Emerald", "primary": "#059669", "secondary": "#022C22", "accent": "#FBBF24", "background": "#ECFDF5", "surface": "#FFFFFF"},
        {"name": "Coral", "primary": "#F43F5E", "secondary": "#1F2937", "accent": "#FB923C", "background": "#FFF1F2", "surface": "#FFFFFF"},
    ],
    "default": [
        {"name": "Classic Blue", "primary": "#2563EB", "secondary": "#0F172A", "accent": "#3B82F6", "background": "#F8FAFC", "surface": "#FFFFFF"},
        {"name": "Forest", "primary": "#15803D", "secondary": "#052E16", "accent": "#EAB308", "background": "#F0FDF4", "surface": "#FFFFFF"},
        {"name": "Plum", "primary": "#9333EA", "secondary": "#1E1B4B", "accent": "#F472B6", "background": "#FAF5FF", "surface": "#FFFFFF"},
        {"name": "Sunset", "primary": "#EA580C", "secondary": "#1C1917", "accent": "#E11D48", "background": "#FFF7ED", "surface": "#FFFFFF"},
    ],
}

# Google Font pairings (heading, body)
FONT_PAIRS: List[Dict[str, str]] = [
    {"heading": "Playfair Display", "body": "Inter"},
    {"heading": "Poppins", "body": "Poppins"},
    {"heading": "Montserrat", "body": "Open Sans"},
    {"heading": "DM Serif Display", "body": "DM Sans"},
    {"heading": "Space Grotesk", "body": "Inter"},
    {"heading": "Lora", "body": "Nunito Sans"},
    {"heading": "Oswald", "body": "Roboto"},
    {"heading": "Plus Jakarta Sans", "body": "Plus Jakarta Sans"},
]

HERO_STYLES = ["centered", "split", "dark", "left"]
CARD_STYLES = ["bordered", "shadow", "filled"]
BUTTON_SHAPES = {"pill": 9999, "rounded": 10, "square": 2}
RADIUS_OPTIONS = [4, 12, 20]
SECTION_ORDERS = [
    ["services", "about", "gallery", "map", "contact"],
    ["about", "services", "gallery", "map", "contact"],
    ["services", "gallery", "about", "map", "contact"],
    ["about", "gallery", "services", "contact", "map"],
]


def get_category_group(category: str) -> str:
    """Map a free-text business category onto a design group."""
    cat_lower = (category or "").lower()
    for group, keywords in CATEGORY_GROUPS.items():
        if any(k in cat_lower for k in keywords):
            return group
    return "default"


def _pick(options: List[Any], seed_bytes: bytes, index: int) -> Any:
    """Pick an option using one byte of the seed digest."""
    return options[seed_bytes[index] % len(options)]


def pick_design(seed: str, category: str, index: Optional[int] = None) -> Dict[str, Any]:
    """
    Select a complete design theme for a lead.
    With an `index` (the lead's position among generated prototypes) the main
    layout choices rotate, so consecutive prototypes never share a hero layout,
    palette or section order. Without it, choices are derived from the seed hash.
    The same inputs always yield the same design.
    """
    digest = hashlib.sha256((seed or "").encode("utf-8")).digest()
    group = get_category_group(category)
    palettes = GROUP_PALETTES[group]

    if index is None:
        palette = dict(_pick(palettes, digest, 0))
        hero_style = _pick(HERO_STYLES, digest, 2)
        card_style = _pick(CARD_STYLES, digest, 3)
        section_order = _pick(SECTION_ORDERS, digest, 6)
    else:
        palette = dict(palettes[index % len(palettes)])
        hero_style = HERO_STYLES[index % len(HERO_STYLES)]
        card_style = CARD_STYLES[index % len(CARD_STYLES)]
        section_order = SECTION_ORDERS[index % len(SECTION_ORDERS)]
    shape_name = _pick(list(BUTTON_SHAPES.keys()), digest, 4)

    return {
        "group": group,
        "index": index,
        "theme_name": palette.pop("name"),
        "palette": palette,
        "fonts": _pick(FONT_PAIRS, digest, 1),
        "hero_style": hero_style,
        "card_style": card_style,
        "button_radius": BUTTON_SHAPES[shape_name],
        "radius": _pick(RADIUS_OPTIONS, digest, 5),
        "section_order": section_order,
    }


def short_business_name(name: str, max_len: int = 32) -> str:
    """
    Brand part of a scraped listing name, e.g.
    "Xia Rooftop Bistro – A Multi Cuisine Veg Restaurant" -> "Xia Rooftop Bistro".
    """
    short = (name or "").strip()
    for sep in (" – ", " — ", " - ", " | ", ": ", ", "):
        if sep in short:
            short = short.split(sep)[0].strip()
    if len(short) > max_len:
        short = short[:max_len].rsplit(" ", 1)[0] + "…"
    return short or name
