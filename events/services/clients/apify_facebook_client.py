"""Apify-backed client that fetches Facebook events via an Apify Actor."""

from __future__ import annotations

import logging
from typing import Iterable, Mapping, Sequence

from apify_client import ApifyClient
from django.conf import settings

from .base import BaseEventClient

logger = logging.getLogger(__name__)


class ApifyFacebookClient(BaseEventClient):
    """Uses Apify to scrape Facebook events for the requested cities."""

    provider_name = "apify_facebook_events"
    DEFAULT_CITIES = ("Johannesburg", "Pretoria")

    def __init__(
        self,
        api_token: str | None = None,
        actor_id: str | None = None,
        max_events: int | None = None,
        cities: Sequence[str] | None = None,
        **config,
    ) -> None:
        super().__init__(**config)
        self.api_token = api_token or settings.APIFY_TOKEN
        self.actor_id = actor_id or settings.APIFY_ACTOR_ID
        self.max_events = max_events or settings.APIFY_MAX_EVENTS
        requested = cities or config.get("queries")
        self.cities: list[str] = [
            city.strip() for city in (requested or self.DEFAULT_CITIES) if city.strip()
        ]
        if not self.api_token:
            raise ValueError("APIFY_TOKEN is required to use the Apify provider.")
        if not self.actor_id:
            raise ValueError("APIFY_ACTOR_ID is required to use the Apify provider.")
        self.client = ApifyClient(self.api_token)

    def fetch(self) -> Iterable[Mapping[str, object]]:
        """Execute the actor per city and yield raw dataset items."""
        actor = self.client.actor(self.actor_id)
        for city in self.cities:
            run_input = {
                "searchQueries": [city],
                "startUrls": [],
                "maxEvents": self.max_events,
            }
            try:
                run = actor.call(run_input=run_input)
            except Exception as exc:  # pragma: no cover - network failure
                logger.error("Apify actor call failed for %s: %s", city, exc)
                continue

            dataset_id = run.get("defaultDatasetId")
            if not dataset_id:
                logger.warning("Apify run for %s returned no dataset ID", city)
                continue

            dataset_client = self.client.dataset(dataset_id)
            for item in dataset_client.iterate_items():
                yield {
                    "apify_raw_item": item,
                    "fallback_city": city,
                }


__all__ = ["ApifyFacebookClient"]
