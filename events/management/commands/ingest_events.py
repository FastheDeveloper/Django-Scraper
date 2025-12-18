import os
from typing import Sequence

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError, CommandParser

from events.services.ingestion import ingest_with_report

PROVIDERS = ("fixtures", "google", "apify_facebook")


class Command(BaseCommand):
    help = "Ingest events using fixtures, Google, or Apify providers."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--city",
            action="append",
            dest="cities",
            help="Restrict ingestion to one or more canonical city names.",
        )
        parser.add_argument(
            "--source",
            choices=PROVIDERS,
            default=os.getenv("EVENT_PROVIDER", "fixtures"),
            help="Provider to use for ingestion (defaults to EVENT_PROVIDER).",
        )

    def handle(self, *args, **options):
        provider_key: str = options["source"]
        cities: Sequence[str] | None = options.get("cities")
        city_filters = (
            [city.strip() for city in cities if city and city.strip()]
            if cities
            else None
        )

        client = self._build_client(provider_key, city_filters)

        allowed_cities = (
            {city.title() for city in city_filters} if city_filters else None
        )

        report = ingest_with_report(client, allowed_cities=allowed_cities)

        summary = (
            f"Created: {report.created}, "
            f"Updated: {report.updated}, "
            f"Skipped: {report.skipped}, "
            f"Errors: {len(report.errors)}"
        )
        self.stdout.write(self.style.SUCCESS(summary))

        if allowed_cities:
            self.stdout.write(f"Cities processed: {', '.join(sorted(allowed_cities))}")

        if report.errors:
            for error in report.errors:
                self.stderr.write(self.style.ERROR(error))

    def _build_client(self, provider_key: str, cities: Sequence[str] | None):
        if provider_key == "fixtures":
            from events.services.clients.fixture_client import FixtureEventClient

            return FixtureEventClient()
        if provider_key == "google":
            from events.services.clients.google_client import GoogleEventClient

            api_key = os.getenv("GOOGLE_API_KEY")
            cse_id = os.getenv("GOOGLE_CSE_ID")
            if not api_key or not cse_id:
                raise CommandError(
                    "GOOGLE_API_KEY and GOOGLE_CSE_ID environment variables are required."
                )
            return GoogleEventClient(api_key=api_key, cse_id=cse_id)
        if provider_key == "apify_facebook":
            from events.services.clients.apify_facebook_client import ApifyFacebookClient

            if not settings.APIFY_TOKEN:
                raise CommandError("APIFY_TOKEN must be configured for Apify ingestion.")
            return ApifyFacebookClient(
                api_token=settings.APIFY_TOKEN,
                actor_id=settings.APIFY_ACTOR_ID,
                max_events=settings.APIFY_MAX_EVENTS,
                cities=cities,
            )
        raise CommandError(f"Unsupported provider '{provider_key}'")
