"""Data cleansing utilities for event payloads."""

from __future__ import annotations

from typing import Any, Mapping


def normalize_event(payload: Mapping[str, Any]) -> Mapping[str, Any]:  # pragma: no cover - placeholder
    """Prepare upstream payloads for storage (implementation pending)."""
    raise NotImplementedError("Event sanitation logic will be implemented later")
