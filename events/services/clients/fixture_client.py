"""Fixture backed client that simulates Google responses."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from .base import BaseEventClient


class FixtureEventClient(BaseEventClient):
    """Loads canned Google-like payloads from the fixtures directory."""

    provider_name = "fixtures"

    def __init__(self, fixtures_dir: Path | None = None, **config: Any) -> None:
        fixtures_base = fixtures_dir or Path(__file__).resolve().parents[2] / "fixtures"
        if not fixtures_base.exists():
            raise FileNotFoundError(f"Fixtures directory not found: {fixtures_base}")
        self.fixtures_dir = fixtures_base
        super().__init__(fixtures_dir=self.fixtures_dir, **config)

    def fetch(self) -> Iterable[Mapping[str, Any]]:
        """Yield raw fixture payloads as dictionaries."""
        for path in sorted(self.fixtures_dir.glob("*.json")):
            with path.open("r", encoding="utf-8") as handle:
                yield json.load(handle)


__all__ = ["FixtureEventClient"]
