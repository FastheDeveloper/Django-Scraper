"""Google Custom Search (CSE) client placeholder."""

from __future__ import annotations

from typing import Any, Iterable, Mapping

import requests

from .base import BaseEventClient


class GoogleEventClient(BaseEventClient):
    provider_name = "google"

    def __init__(self, api_key: str, cse_id: str, **config: Any) -> None:
        super().__init__(api_key=api_key, cse_id=cse_id, **config)
        self.api_key = api_key
        self.cse_id = cse_id

    def fetch(self) -> Iterable[Mapping[str, Any]]:  # pragma: no cover - placeholder
        """Search Google CSE for events (implementation to be added)."""
        raise NotImplementedError("Google ingestion is not implemented yet")


__all__ = ["GoogleEventClient"]
