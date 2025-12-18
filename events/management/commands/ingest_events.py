import os
from typing import Sequence

from django.core.management.base import BaseCommand, CommandParser, CommandError

from events.services.ingestion import ingest_with_report

PROVIDERS = ("fixtures", "google")


class Command(BaseCommand):
    help = "Ingest events using local fixtures or the Google client."

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
        client = self._build_client(provider_key)

        cities: Sequence[str] | None = options.get("cities")
        allowed_cities = (
            {city.strip().title() for city in cities if city.strip()}
            if cities
            else None
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

    def _build_client(self, provider_key: str):
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
        raise CommandError(f"Unsupported provider '{provider_key}'")
