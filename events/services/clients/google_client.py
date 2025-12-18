"""Google API client placeholder."""

from __future__ import annotations

from typing import Any, Iterable, Mapping

from .base import BaseEventClient


class GoogleEventClient(BaseEventClient):
    """Stub client that will eventually hit real Google APIs."""

    provider_name = "google"

    def __init__(self, api_key: str, cse_id: str, **config: Any) -> None:
        super().__init__(api_key=api_key, cse_id=cse_id, **config)
        self.api_key = api_key
        self.cse_id = cse_id

    def fetch(self) -> Iterable[Mapping[str, Any]]:  # pragma: no cover - stub
        raise NotImplementedError(
            "GoogleEventClient will be implemented when API access is available."
        )


__all__ = ["GoogleEventClient"]
