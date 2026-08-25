# Deliveroo Backend

Flask + PostgreSQL API for the Deliveroo courier app.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Fill in `.env` with your real database connection string and a JWT secret:
```
DATABASE_URL=postgresql://user:password@host/dbname
JWT_SECRET_KEY=<any long random string>
```

## Run locally

```bash
flask run
```

Visit `http://localhost:5000/` — should return `{"status": "ok", "service": "deliveroo-backend"}`.

## Status
Project scaffolding only — models, auth, and parcel/admin endpoints not yet built. See `deliveroo-backend-plan.md` for the full build plan.
