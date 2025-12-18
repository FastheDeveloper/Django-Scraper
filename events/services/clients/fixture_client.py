"""Loads canned event payloads from the local fixtures directory."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Mapping

from .base import BaseEventClient


class FixtureEventClient(BaseEventClient):
    provider_name = "fixtures"

    def __init__(self, fixtures_dir: Path | None = None, **config: Any) -> None:
        super().__init__(fixtures_dir=fixtures_dir, **config)
        self.fixtures_dir = fixtures_dir or Path(__file__).resolve().parents[2] / "fixtures"

    def fetch(self) -> Iterable[Mapping[str, Any]]:  # pragma: no cover - placeholder
        """Return fixture payloads once they exist."""
        raise NotImplementedError("Fixture ingestion is not implemented yet")


__all__ = ["FixtureEventClient"]
