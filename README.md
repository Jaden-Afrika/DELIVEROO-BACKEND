# Deliveroo Backend

Flask + PostgreSQL API for the Deliveroo courier app.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### Django authentication API

The custom Django `accounts` app is configured with email-based login and JWT
authentication. Apply its migrations and start the Django API with:

```bash
python manage.py migrate
python manage.py runserver 8000
```

Authentication endpoints are available under `/api/auth/` (`signup`, `login`,
`token/refresh`, `logout`, and `me`).

### Database (Docker)

```bash
docker compose up -d
```

### Migrate & Seed

```bash
flask db migrate -m "initial migration"
flask db upgrade
python -m scripts.seed
```

### Run

```bash
flask run
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
app.py                  # Flask entry point, create_app factory
app/
  config.py             # Config classes
  extensions.py         # db, migrate, jwt, cors singletons
  errors.py             # Error handlers
  models/               # SQLAlchemy models
  schemas/              # Marshmallow request/response schemas
  routes/               # Blueprint route handlers
  services/             # Business logic & adapter interfaces
tests/                  # Pytest suite
scripts/seed.py         # Idempotent seed script
migrations/             # Flask-Migrate / Alembic
```

## API Endpoints

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
