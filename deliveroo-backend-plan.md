# Deliveroo Backend — Build Plan

Flask + PostgreSQL, in a separate repo from the frontend. This plan assumes one person (or a small pair) building it, matching the field names and endpoints the frontend already expects.

---

## Phase 1 — Project setup
- [ ] Create the repo (`deliveroo-backend`), initialize git
- [ ] Set up virtual environment, install: `flask`, `flask-sqlalchemy`, `flask-migrate`, `flask-jwt-extended`, `flask-cors`, `psycopg2-binary`, `python-dotenv`, `gunicorn`
- [ ] Freeze dependencies to `requirements.txt`
- [ ] Create `.env.example` with `DATABASE_URL` and `JWT_SECRET_KEY` placeholders, `.gitignore` for `.venv/`, `.env`, `__pycache__/`
- [ ] Stand up the Postgres database on Neon (free tier, no card) — get the connection string
- [ ] First commit, push to GitHub

## Phase 2 — Database models
- [ ] `User` model: id, name, email (unique), password_hash, role (`user`/`admin`, default `user`), created_at
- [ ] `Parcel` model: id, pickup_location, destination, weight_category, distance_km, price, status (`pending`/`in_transit`/`delivered`, default `pending`), current_location, owner_id (FK → users), created_at
- [ ] `to_dict()` method on each model — confirm exact field-name casing against the frontend's `parcelsAPI.js` before writing this (don't assume camelCase, check)
- [ ] Run `flask db init`, generate and apply the first migration
- [ ] Confirm tables exist on Neon (Neon's SQL editor, `\dt` or a `SELECT`)

## Phase 3 — Auth
- [ ] `POST /auth/signup` — hash password (werkzeug or bcrypt), create user, return JWT
- [ ] `POST /auth/login` — verify credentials, return JWT
- [ ] JWT payload includes `role`, since `RequireAdmin` on the frontend checks that
- [ ] Test both endpoints with curl/Postman before moving on

## Phase 4 — Parcel endpoints (user-facing)
- [ ] `POST /parcels` — create parcel; `owner_id` comes from the JWT, never from the request body
- [ ] `GET /parcels/me` — list the logged-in user's parcels
- [ ] `GET /parcels/:id` — get one parcel's details
- [ ] `PATCH /parcels/:id/destination` — enforce server-side: only the owner, only if `status != "delivered"`
- [ ] Cancel endpoint (`DELETE` or a status-based patch) — same two rules, enforced server-side not just trusted from the frontend

## Phase 5 — Admin endpoints
- [ ] `GET /admin/parcels` — list every parcel; require `role == "admin"` from the JWT
- [ ] `PATCH /admin/parcels/:id/status`
- [ ] `PATCH /admin/parcels/:id/location`
- [ ] Confirm these paths match exactly what `adminAPI.js` on the frontend calls

## Phase 6 — Wire it to the real frontend
- [ ] Enable CORS for the frontend's actual origin (not `*`, once you know the Vercel URL)
- [ ] Set the frontend's `.env` to point `VITE_API_BASE_URL`/`VITE_API_URL` (check which name `client.js` actually uses) at this backend
- [ ] Run both together locally: sign up → create a parcel → see it in "My Parcels" → change its status as admin → confirm it updates
- [ ] Fix any field-name mismatches this surfaces — this is where most bugs will show up

## Phase 7 — Deploy
- [ ] Deploy to Render or Railway (both have working free tiers for small Flask apps)
- [ ] Set `DATABASE_URL` and `JWT_SECRET_KEY` as environment variables on the host, not in code
- [ ] Run the migration against production once deployed
- [ ] Point the deployed frontend's env var at the deployed backend URL, redeploy frontend if needed
- [ ] Full QA pass against the live, deployed pair — not just localhost

## Phase 8 — Buffer / polish
- [ ] Error handling — consistent JSON error responses instead of raw stack traces
- [ ] Basic input validation on every endpoint (missing fields, invalid weight_category, etc.)
- [ ] Quick look at whether `/orders` vs `/parcels` naming got settled on the frontend side — rename endpoints to match if needed

---

## Open dependency
This plan assumes the frontend's exact field names and endpoint shapes are the source of truth. Before Phase 2, actually open `parcelsAPI.js` and `adminAPI.js` in the frontend repo and copy the real field names/paths in — don't work from memory of what they "probably" are.
