# Events API Scaffold

This repository contains a lightweight Django + Django REST Framework project that will power the events ingestion and API assessment. The codebase focuses on clean defaults, environment-driven configuration, and ready-to-extend service layers.

## Requirements

- macOS with Python 3.11+
- SQLite (ships with Python)

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # then fill in secrets
python manage.py migrate
python manage.py runserver
```

### Virtual environment notes

The project expects a local `.venv/` that stays next to the source tree. The commands above use the system `python` to create and activate it. Always re-run `source .venv/bin/activate` in new shells before working on the project.

## Environment variables

Environment variables are loaded from a `.env` file at the project root using [`python-dotenv`](https://github.com/theskumar/python-dotenv). The `.env.example` file documents every required key:

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `EVENT_PROVIDER`
- `GOOGLE_API_KEY`
- `GOOGLE_CSE_ID`

Copy `.env.example` to `.env`, fill in the secrets, and the settings module will load them automatically on startup.

## Project structure

```
.
├── config/              # Django project (settings, URLs, WSGI)
├── events/              # Events application
│   ├── fixtures/        # Placeholder for local fixture payloads
│   └── services/
│       ├── clients/     # Fixture + Google client stubs
│       ├── ingestion.py # Orchestration placeholder
│       └── sanitation.py# Normalization placeholder
├── manage.py
├── pyproject.toml       # Ruff + Black configuration
├── requirements.txt
└── README.md
```

## API surface

`/api/health` returns `{ "status": "ok" }` and proves the stack is wired. Mount future API endpoints beneath the `/api/` prefix via `events.urls`.

## Code quality

- **Black** keeps formatting consistent: `black .`
- **Ruff** handles linting and import order: `ruff check .`

## Next steps

- Implement ingestion strategies inside `events/services/`
- Flesh out DRF serializers/viewsets for delivering event data via `/api/`
