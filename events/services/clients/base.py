"""Common interfaces for communicating with external event providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Iterable, Mapping


class BaseEventClient(ABC):
    """Defines an interface all event provider clients should implement."""

    provider_name = "base"

    def __init__(self, **config: Any) -> None:
        self.config = config

    @abstractmethod
    def fetch(self) -> Iterable[Mapping[str, Any]]:
        """Retrieve raw event payloads from an upstream provider."""


__all__ = ["BaseEventClient"]
