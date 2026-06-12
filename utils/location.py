"""Geographic helpers for map previews and location display."""

from __future__ import annotations

# Approximate state centroids (lat, lon) for India map previews.
STATE_COORDINATES: dict[str, tuple[float, float]] = {
    "Andaman and Nicobar Islands": (11.7401, 92.6586),
    "Andhra Pradesh": (15.9129, 79.74),
    "Arunachal Pradesh": (28.218, 94.7278),
    "Assam": (26.2006, 92.9376),
    "Bihar": (25.0961, 85.3131),
    "Chandigarh": (30.7333, 76.7794),
    "Chhattisgarh": (21.2787, 81.8661),
    "Dadra and Nagar Haveli": (20.1809, 73.0169),
    "Goa": (15.2993, 74.124),
    "Gujarat": (23.0225, 72.5714),
    "Haryana": (29.0588, 76.0856),
    "Himachal Pradesh": (31.1048, 77.1734),
    "Jammu and Kashmir": (33.7782, 76.5762),
    "Jharkhand": (23.6102, 85.2799),
    "Karnataka": (15.3173, 75.7139),
    "Kerala": (10.8505, 76.2711),
    "Madhya Pradesh": (22.9734, 78.6569),
    "Maharashtra": (19.7515, 75.7139),
    "Manipur": (24.6637, 93.9063),
    "Meghalaya": (25.467, 91.3662),
    "Mizoram": (23.1645, 92.9376),
    "Nagaland": (26.1584, 94.5624),
    "Odisha": (20.9517, 85.0985),
    "Puducherry": (11.9416, 79.8083),
    "Punjab": (31.1471, 75.3412),
    "Rajasthan": (27.0238, 74.2179),
    "Sikkim": (27.533, 88.5122),
    "Tamil Nadu": (11.1271, 78.6569),
    "Telangana": (18.1124, 79.0193),
    "Tripura": (23.9408, 91.9882),
    "Uttar Pradesh": (26.8467, 80.9462),
    "Uttarakhand": (30.0668, 79.0193),
    "West Bengal": (22.9868, 87.855),
}

INDIA_CENTER = (20.5937, 78.9629)


def _normalize_name(name: str) -> str:
    return name.strip()


def _resolve_state_key(state: str) -> str | None:
    normalized = _normalize_name(state)
    if normalized in STATE_COORDINATES:
        return normalized
    for key in STATE_COORDINATES:
        if key.lower() == normalized.lower():
            return key
    return None


def get_coordinates(state: str, district: str = "") -> tuple[float, float]:
    """Return map coordinates for a district, falling back to state or India center."""
    state_key = _resolve_state_key(state)
    base = STATE_COORDINATES.get(state_key or "", INDIA_CENTER)

    district = _normalize_name(district)
    if not district:
        return base

    # Spread districts slightly around the state centroid when exact coords are unavailable.
    offset_seed = sum(ord(char) for char in district)
    lat_offset = ((offset_seed % 17) - 8) * 0.08
    lon_offset = ((offset_seed % 23) - 11) * 0.08
    return (base[0] + lat_offset, base[1] + lon_offset)


def format_location_pins(state: str, district: str) -> str:
    """Return a short multi-line location label for display."""
    state = _normalize_name(state)
    district = _normalize_name(district)
    lines = []
    if state:
        lines.append(f"📍 {state}")
    if district:
        lines.append(f"📍 {district}")
    lines.append("📍 India")
    return "\n".join(lines)
