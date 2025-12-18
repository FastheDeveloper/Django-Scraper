"""Coordinated ingestion workflows for event providers."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Iterable, Mapping, Sequence

from django.db import transaction

from events.models import Event

from .clients.base import BaseEventClient
from .sanitation import normalize_cse_item, normalize_places_item


@dataclass
class IngestionReport:
    """Aggregated ingestion stats and affected records."""

    events: list[Event] = field(default_factory=list)
    created: int = 0
    updated: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)


def ingest(client: BaseEventClient) -> list[Event]:
    """Fetch, normalize, and upsert events for the provided client."""
    return ingest_with_report(client).events


def ingest_with_report(
    client: BaseEventClient, allowed_cities: Sequence[str] | None = None
) -> IngestionReport:
    """Run ingestion, optionally restricting to cities, and return stats."""
    allowed = {city.strip() for city in allowed_cities} if allowed_cities else None
    report = IngestionReport()
    with transaction.atomic():
        for payload in client.fetch():
            for data in iter_normalized(payload):
                if allowed and data["city"] not in allowed:
                    report.skipped += 1
                    continue
                if not data["title"] or not data["city"]:
                    report.skipped += 1
                    continue
                try:
                    event, created = upsert_event(data)
                except Exception as exc:  # pragma: no cover - defensive
                    report.errors.append(f"{data.get('title') or 'unknown'}: {exc}")
                else:
                    report.events.append(event)
                    if created:
                        report.created += 1
                    else:
                        report.updated += 1
    return report


def iter_normalized(payload: Mapping[str, object]) -> Iterable[Mapping[str, object]]:
    """Yield normalized dictionaries from a payload chunk."""
    if "results" in payload:
        for item in payload["results"]:
            yield normalize_places_item(item)
    elif "items" in payload:
        for item in payload["items"]:
            yield normalize_cse_item(item)


def upsert_event(data: Mapping[str, object]) -> tuple[Event, bool]:
    """Create or update an event, preserving raw payload."""
    source = data["source"]
    event_url = data.get("event_url")
    fingerprint = fingerprint_event(data) if not event_url else None
    defaults = {
        "title": data["title"],
        "start_date": data["start_date"],
        "venue_name": data["venue_name"],
        "city": data["city"],
        "category": data["category"],
        "event_url": event_url,
        "raw_payload": data["raw_payload"],
        "fingerprint": fingerprint,
        "source": source,
    }
    if event_url:
        event, created = Event.objects.update_or_create(
            source=source, event_url=event_url, defaults=defaults
        )
    else:
        event, created = Event.objects.update_or_create(
            source=source, fingerprint=fingerprint, defaults=defaults
        )
    return event, created


def fingerprint_event(data: Mapping[str, object]) -> str:
    """Compute a deterministic fingerprint for URL-less events."""
    start_value = data.get("start_date")
    iso_start = start_value.isoformat() if start_value else ""
    components = [
        data.get("title") or "",
        iso_start,
        data.get("venue_name") or "",
        data.get("city") or "",
        data.get("category") or "",
    ]
    joined = "|".join(components)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


__all__ = ["ingest", "ingest_with_report", "IngestionReport"]
