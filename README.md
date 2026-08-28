# Deliveroo Backend

Django (DRF) + PostgreSQL API for the Deliveroo courier app.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### Database (Docker)

```bash
docker compose up -d
```

### Migrate & Seed

```bash
python manage.py migrate
python -m scripts.seed
```

### Run

```bash
python manage.py runserver 0.0.0.0:5000
```

Visit `http://localhost:5000/` — returns `{"status": "ok", "service": "deliveroo-backend"}`.

### Health

- `GET /` — `{"status": "ok", "service": "deliveroo-backend"}`
- `GET /health` — same
- `GET /openapi.json` — OpenAPI spec

### Test accounts (dev only)

| Role  | Email                | Password    |
|-------|----------------------|-------------|
| user  | user@deliveroo.dev   | password123 |
| admin | admin@deliveroo.dev  | password123 |

### Run tests

```bash
pytest -v
```

## Architecture

```
manage.py                # Django management entry point
config/
  settings.py            # Django settings
  test_settings.py       # Settings for the test suite (SQLite)
  urls.py                # Root URL configuration
  wsgi.py                # WSGI application
app/                     # Django app
  models/                # Django models (users, parcels, addresses, ...)
  serializers.py         # DRF request/response serializers
  views.py               # API views
  urls.py                # URL routes
  exceptions.py          # Custom exception handler & error shapes
  services/              # Business logic & adapter interfaces
tests/                   # Pytest suite
scripts/seed.py          # Idempotent seed script
app/migrations/          # Django migrations
```

## API Endpoints

### API documentation (Swagger/OpenAPI)

Generated from the code via drf-spectacular:

- `/api/docs/` — interactive Swagger UI
- `/api/redoc/` — Redoc UI
- `/api/schema/` — raw OpenAPI schema (YAML)
- `/api/schema/openapi.json` — raw OpenAPI schema (JSON)

### Auth
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/signup` | No | Register |
| POST | `/auth/login` | No | Log in |
| POST | `/auth/logout` | Yes | Log out |
| GET | `/auth/me` | Yes | Current user |

### Parcels
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/parcels/me` | Yes | List user parcels |
| POST | `/parcels` | Yes | Create parcel |
| GET | `/parcels/<id>` | Yes | Get parcel |
| PATCH | `/parcels/<id>/destination` | Yes | Update destination |
| PATCH | `/parcels/<id>/cancel` | Yes | Cancel parcel |
| GET | `/parcels/<id>/status-history` | Yes | Status history |
| GET | `/parcels/<id>/tracking` | Yes | Tracking |

### Admin
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/admin/parcels` | Admin | List all parcels |
| PATCH | `/admin/parcels/<id>/status` | Admin | Update status |
| PATCH | `/admin/parcels/<id>/location` | Admin | Update location |

### System
| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Health check |
| GET | `/health` | Health check |
| GET | `/openapi.json` | OpenAPI spec |
