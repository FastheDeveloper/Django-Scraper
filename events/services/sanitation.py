"""Data cleansing utilities for event payloads."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Mapping, MutableMapping
from urllib.parse import urlparse, urlunparse

from dateutil import parser

CITY_KEYWORDS = {
    "johannesburg": "Johannesburg",
    "joburg": "Johannesburg",
    "jhb": "Johannesburg",
    "soweto": "Johannesburg",
    "rosebank": "Johannesburg",
    "melville": "Johannesburg",
    "pretoria": "Pretoria",
    "pta": "Pretoria",
    "tshwane": "Pretoria",
}


def normalize_places_item(raw: Mapping[str, Any]) -> dict[str, Any]:
    """Normalize a Google Places-style entry."""
    metadata = {
        "title": clean_title(raw.get("name")),
        "start_date": parse_datetime(raw.get("start_time")),
        "venue_name": clean_title(raw.get("venue")),
        "city": normalize_city(raw.get("city") or raw.get("formatted_address")),
        "category": derive_category(raw.get("types")),
        "event_url": normalize_url(raw.get("website")),
        "source": raw.get("source", "google_places"),
        "raw_payload": dict(raw),
    }
    return metadata


def normalize_cse_item(raw: Mapping[str, Any]) -> dict[str, Any]:
    """Normalize a Google CSE-style entry."""
    metatag = extract_metatag(raw)
    metadata = {
        "title": clean_title(raw.get("title")),
        "start_date": parse_datetime(metatag.get("event:start_time")),
        "venue_name": clean_title(metatag.get("event:venue_name")),
        "city": normalize_city(metatag.get("event:location")),
        "category": clean_title(metatag.get("event:category")),
        "event_url": normalize_url(raw.get("link")),
        "source": raw.get("source", "google_cse"),
        "raw_payload": dict(raw),
    }
    return metadata


def extract_metatag(raw: Mapping[str, Any]) -> MutableMapping[str, Any]:
    pagemap = raw.get("pagemap") or {}
    metatags = pagemap.get("metatags") or []
    if metatags:
        return dict(metatags[0])
    return {}


def normalize_city(value: Any) -> str:
    if not value or not isinstance(value, str):
        return ""
    cleaned = re.sub(r"[^a-z0-9 ]+", " ", value.lower())
    for keyword, canonical in CITY_KEYWORDS.items():
        if keyword in cleaned:
            return canonical
    return " ".join(part.capitalize() for part in value.strip().split())


def parse_datetime(value: Any) -> datetime | None:
    if not value or not isinstance(value, str):
        return None
    try:
        dt = parser.isoparse(value)
    except (ValueError, TypeError):
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def clean_title(value: Any) -> str:
    if not value or not isinstance(value, str):
        return ""
    compact = re.sub(r"\s+", " ", value).strip()
    return compact


def derive_category(types: Any) -> str:
    if isinstance(types, (list, tuple)):
        for item in types:
            if isinstance(item, str) and item:
                return clean_title(item.replace("_", " "))
    if isinstance(types, str):
        return clean_title(types)
    return ""


def normalize_url(value: Any) -> str | None:
    if not value or not isinstance(value, str):
        return None
    candidate = value.strip()
    if not candidate:
        return None
    if "://" not in candidate:
        candidate = f"https://{candidate}"
    parsed = urlparse(candidate)
    scheme = parsed.scheme if parsed.scheme in {"http", "https"} else "https"
    netloc = parsed.netloc or parsed.path
    path = parsed.path if parsed.netloc else ""
    normalized = urlunparse((scheme, netloc, path, "", "", ""))
    return normalized or None


__all__ = [
    "normalize_places_item",
    "normalize_cse_item",
    "normalize_city",
    "clean_title",
    "normalize_url",
]
