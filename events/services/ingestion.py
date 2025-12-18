"""Coordinated ingestion workflows for event providers."""

from __future__ import annotations

from typing import Iterable, Mapping

from .clients.base import BaseEventClient


def ingest(client: BaseEventClient) -> Iterable[Mapping[str, object]]:  # pragma: no cover - placeholder
    """Kick off an ingestion run using the provided client."""
    raise NotImplementedError("Ingestion orchestration will be implemented later")
