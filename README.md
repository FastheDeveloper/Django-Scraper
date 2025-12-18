# Events API Scaffold

This repository is a take-home friendly Django + Django REST Framework backend that ingests public events for Johannesburg and Pretoria using fixture data that mimics Google Places / Custom Search responses. The goal is to demonstrate ingestion, sanitation, dedupe, and API exposure, with a clear path to swap fixtures for real Google clients later.

## Requirements

- macOS with Python 3.11+
- SQLite (included with Python)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # then fill in values below
python manage.py migrate
python manage.py ingest_events --city Johannesburg --city Pretoria --source fixtures
python manage.py runserver
```

### Environment variables

Django loads configuration from `.env` via `python-dotenv`. Required settings:

| Key | Description |
| --- | --- |
| `DJANGO_SECRET_KEY` | Any non-empty string for dev |
| `DJANGO_DEBUG` | `true`/`false` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated list (e.g. `127.0.0.1,localhost`) |
| `EVENT_PROVIDER` | `fixtures`, `google`, or `apify_facebook` |
| `GOOGLE_API_KEY` | Placeholder for future Google client |
| `GOOGLE_CSE_ID` | Placeholder for future Google client |
| `APIFY_TOKEN` | Required when using Apify |
| `APIFY_ACTOR_ID` | Defaults to `UZBnerCFBo5FgGouO` |
| `APIFY_MAX_EVENTS` | Max results per Apify actor run (default `30`) |

Fixture-only development only needs the first four keys; Google keys will be used once real API integration is enabled.

### Project structure

```
.
├── config/                   # Django project settings + URL routing
├── events/
│   ├── fixtures/             # Google-shaped sample payloads
│   ├── management/commands/  # ingest_events command
│   ├── services/             # clients, sanitation, ingestion orchestration
│   ├── serializers.py        # Event DRF serializer
│   ├── urls.py               # /api routes
│   └── views.py              # Health + List endpoints
├── manage.py
├── requirements.txt
└── README.md
```

## Ingestion

Use the management command to populate the `Event` table from fixtures:

```bash
python manage.py ingest_events --city Johannesburg --city Pretoria --source fixtures
```

The command is idempotent and prints a summary of created/updated/skipped rows. You can omit the `--city` flags to ingest all supported cities. Once real Google credentials are available, switch providers via `EVENT_PROVIDER=google` or `--source google` and ensure `GOOGLE_API_KEY` + `GOOGLE_CSE_ID` are set in the environment.

### Apify ingestion (Facebook events)

1. Set the Apify credentials in `.env` (or export them):
   ```env
   EVENT_PROVIDER=apify_facebook
   APIFY_TOKEN=<your-apify-token>
   APIFY_ACTOR_ID=UZBnerCFBo5FgGouO  # override only if advised by HR
   APIFY_MAX_EVENTS=30               # tweak to limit dataset size
   ```
2. Run the management command, optionally scoping cities:
   ```bash
   python manage.py ingest_events --city Johannesburg --city Pretoria --source apify_facebook
   ```
3. Verify data via the API (should now show `"source": "apify_facebook_events"`):
   ```bash
   curl "http://127.0.0.1:8000/api/events?city=Johannesburg"
   ```

Fixtures remain available (set `EVENT_PROVIDER=fixtures`) so reviewers without an Apify token can still run the project.

### Railway deployment quick-test

When deployed on Railway (using the baked Dockerfile + Postgres), bootstrap the remote database with:

```bash
railway run python manage.py migrate
railway run python manage.py ingest_events --city Johannesburg --city Pretoria --source apify_facebook
```

Then hit the hosted API, e.g.:

```
https://django-scraper-production-0c4d.up.railway.app/api/events?city=Johannesburg&page_size=10

Need to fall back to fixtures remotely? Swap the source flag:

```bash
railway run python manage.py ingest_events --city Johannesburg --city Pretoria --source fixtures
```
```

## API usage

- `GET /api/health` → `{ "status": "ok" }`
- `GET /api/events` → paginated events (10 per page). Supports query params:
  - `?page=2`
  - `?page_size=20`
  - `?city=Johannesburg` (case-insensitive)

Example request:

```bash
curl "http://127.0.0.1:8000/api/events?city=Pretoria&page_size=5"
```

## Code quality & tooling

- Format with **Black**: `black .`
- Lint with **Ruff**: `ruff check .`

## Switching to Google later

The ingestion workflow is driven by a provider interface (`events/services/clients/base.py`). Today, `FixtureEventClient` feeds local JSON. To move to real Google requests:

1. Implement the HTTP logic inside `GoogleEventClient`.
2. Set `EVENT_PROVIDER=google`, `GOOGLE_API_KEY`, and `GOOGLE_CSE_ID` in `.env`.
3. Run `python manage.py ingest_events --source google` to fetch live data.

The rest of the pipeline (sanitation, dedupe, API) stays unchanged.
