from django.db import models
from django.db.models import Q


class Event(models.Model):
    """Normalized event representation persisted after ingestion."""

    title = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    venue_name = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    category = models.CharField(max_length=100, blank=True)
    event_url = models.URLField(max_length=500, blank=True, null=True)
    source = models.CharField(max_length=50)
    raw_payload = models.JSONField()
    fingerprint = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        help_text="Deterministic hash used to deduplicate records without URLs.",
    )

    class Meta:
        ordering = ["-start_date", "title"]
        indexes = [
            models.Index(fields=["city"], name="event_city_idx"),
            models.Index(fields=["start_date"], name="event_start_date_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["source", "event_url"],
                condition=Q(event_url__isnull=False),
                name="event_unique_source_url",
            ),
            models.UniqueConstraint(
                fields=["source", "fingerprint"],
                condition=Q(event_url__isnull=True) & Q(fingerprint__isnull=False),
                name="event_unique_source_fingerprint",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.city})"
