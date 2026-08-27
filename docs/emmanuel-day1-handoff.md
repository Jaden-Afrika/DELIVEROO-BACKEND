# Emmanuel Day 1 Handoff — Parcel Details & Changes Backend

## Branch

`feature/emmanuel-parcel-details-backend`

## Starting Commit

`e235433` (Set up Flask backend project structure) + uncommitted scaffold from `backend-scaffold` branch

## Files Changed

| File | Change |
|------|--------|
| `app/models/parcel.py` | Enhanced `to_dict()`: added `estimatedTravelTime`, `cancelledAt`, `deliveredAt`, `currency` fields; added `_estimated_travel_minutes()` helper |
| `app/routes/parcels.py` | Rewrote all endpoints: added admin access, status history creation, transaction wrapping, structured error codes, geocoding/routing recalculation on destination change |
| `app/routes/admin.py` | Added status history creation on status updates, consistent error format, used `db.session.get()` instead of deprecated `Query.get()` |
| `tests/conftest.py` | Added `other` user fixture + `other_token`/`other_header` fixtures for non-owner access tests |
| `tests/test_parcel_details.py` | **New file:** 30 comprehensive tests covering detail, destination, cancel, status history, route registration |
| `tests/test_parcels_routes.py` | Updated `test_cancel_other_users_parcel` to use `other_header` (non-admin) instead of admin |
| `docs/frontend-api-contract.md` | Expanded with detailed request/response shapes, field documentation, status history format, decisions |

## Endpoints Implemented

| Method | Path | Auth | Status |
|--------|------|------|--------|
| `GET` | `/parcels/<id>` | Owner or admin | **Fully implemented** — returns complete parcel detail with all frontend fields |
| `PATCH` | `/parcels/<id>/destination` | Owner or admin | **Fully implemented** — validates, recalculates distance/price via services, records status history |
| `PATCH` | `/parcels/<id>/cancel` | Owner or admin | **Fully implemented** — soft cancel, records `cancelled_at`, creates status history atomically |
| `GET` | `/parcels/<id>/status-history` | Owner or admin | **Fully implemented** — returns ordered status history |
| `GET` | `/parcels/<id>/tracking` | Owner or admin | 501 stub (deferred) |

## Request/Response Examples

### GET `/parcels/1`

```json
{
  "id": 1,
  "trackingNumber": "DRV-A1B2C3D4",
  "pickupLocation": "Westlands, Nairobi",
  "destination": "Kilimani, Nairobi",
  "weightCategory": "medium",
  "weight": "Medium (2 - 10kg)",
  "distanceKm": 10.0,
  "estimatedTravelTime": 15,
  "price": 600.0,
  "currency": "KES",
  "status": "pending",
  "currentLocation": "Westlands, Nairobi",
  "createdBy": "1",
  "ownerId": "1",
  "ownerName": "Test User",
  "createdAt": "2026-08-25T10:00:00+00:00",
  "dateCreated": "2026-08-25T10:00:00+00:00"
}
```

### PATCH `/parcels/1/destination`

Request:
```json
{"destination": "Lavington, Nairobi"}
```

Response: Same shape as GET, with updated `destination`, `distanceKm`, `price`.

### PATCH `/parcels/1/cancel`

Request: Empty body.

Response: Same shape as GET, with `status: "cancelled"` and `cancelledAt` field.

## Tests Passed

```
73 passed, 161 warnings in 19.58s
```

**Breakdown:**
- `test_parcel_details.py` — 30 tests (new, Day 1)
- `test_parcels_routes.py` — 6 tests (existing, 1 updated)
- `test_admin_routes.py` — 6 tests (existing)
- `test_auth_routes.py` — 9 tests (existing)
- `test_models.py` — 6 tests (existing)
- `test_pricing.py` — 6 tests (existing)
- `test_routes.py` — 1 test (existing)
- `test_services.py` — 5 tests (existing)
- `test_app.py` — 4 tests (existing)

## Migration Status

**Blocked:** PostgreSQL is not available locally. Migration has NOT been run against a real database.

To apply migrations when PostgreSQL is available:
```bash
docker compose up -d
flask db migrate -m "add parcel status history"
flask db upgrade
```

The existing `migrations/` directory is wired. New columns (`cancelled_at`, `delivered_at`) are already in the Parcel model but have NOT been generated into a migration file yet.

## Required Environment Variables

```
DATABASE_URL=postgresql://deliveroo:deliveroo@localhost:5432/deliveroo_dev
JWT_SECRET_KEY=<any long random string>
FRONTEND_ORIGIN=http://localhost:5173
```

## Known Limitations

1. **PostgreSQL migrations not applied** — `cancelled_at` and `delivered_at` columns exist in the model but need a migration. The `parcel_status_history` table also needs migration against PostgreSQL.
2. **`estimatedTravelTime` not used by frontend** — Frontend computes travel time client-side via OSM/OSRM. Backend provides it but frontend ignores it.
3. **`currency` not used by frontend** — Frontend hardcodes `"KSh"`. Backend includes it for completeness.
4. **`ChangeDestinationForm` has no API call** — Frontend's destination change is a synchronous Redux action (local state only). The `PATCH /parcels/<id>/destination` endpoint exists but is not called.
5. **Stub services return deterministic values** — Geocoding returns fixed Nairobi coords, routing returns 10km/25min. Price recalculation works but uses stub distances.
6. **No input sanitization beyond length** — Destination text is not geocoded for validity.

## Accepted Decisions

| Decision | Value | Rationale |
|----------|-------|-----------|
| Destination changes allowed for | All non-delivered/non-cancelled | Product flexibility |
| Price recalculation on destination change | Yes | Distance changes affect price |
| `estimatedTravelTime` unit | Integer minutes | `(distanceKm / 40) * 60` rounded |
| Cancellation method | PATCH | Matches frontend contract |
| Non-owner access failures | 404 (not 403) | Prevents parcel existence leakage |
| Admin access to parcels | Allowed | Admin can view/manage any parcel |

## Tomorrow Checklist (Day 2)

### Must Complete

1. **PostgreSQL migration verification**
   - Start PostgreSQL: `docker compose up -d`
   - Generate migration: `flask db migrate -m "parcel detail fields"`
   - Apply: `flask db upgrade`
   - Verify columns exist: `psql -d deliveroo_dev -c "\d parcels"`

2. **Verify detail timestamps**
   - Confirm `createdAt` and `dateCreated` are valid ISO-8601 UTC
   - Confirm no `Invalid Date` in any response
   - Test with real PostgreSQL timestamps

3. **Verify weight/category serialization**
   - Confirm `weight` contains human-readable label
   - Confirm `weightCategory` contains enum value
   - Test all three categories: light, medium, heavy

4. **Verify price and currency**
   - Confirm `price` is numeric with 2 decimal places
   - Confirm `currency` is `"KES"`
   - Test price recalculation on destination change

5. **Verify cancellation persistence**
   - Cancel parcel → fresh GET → confirms `status: "cancelled"`
   - Cancel parcel → list → confirms cancelled status
   - Confirm `cancelledAt` is present and valid

6. **Verify destination update rules**
   - Delivered → 409 error
   - Cancelled → 409 error
   - Pending → success with recalculated price
   - Empty destination → 422 validation error

7. **Verify status-history behavior**
   - Create parcel → history has "pending" entry
   - Cancel parcel → history has "cancelled" entry
   - Both entries have timestamps and user IDs

8. **Verify OpenAPI matches implementation**
   - Check `/openapi.json` includes all implemented endpoints
   - Verify method signatures match

### Should Verify

9. **Frontend integration test**
   - Start frontend locally
   - Create parcel → view details → change destination → cancel
   - Verify all fields render correctly

10. **Edge cases**
    - Concurrent cancellation (race condition)
    - Very long destination strings
    - Special characters in destination

### Blocked By

- PostgreSQL availability (for migration verification)
- Frontend availability (for integration testing)

## Ready-to-Run Commands

```bash
# Activate venv
source .venv/bin/activate

# Set environment
export DATABASE_URL=sqlite:///:memory:
export JWT_SECRET_KEY=test-secret-key-32-chars-long!!

# Run all tests
pytest -v

# Run only parcel detail tests
pytest tests/test_parcel_details.py -v

# Start API locally (needs PostgreSQL)
docker compose up -d
export DATABASE_URL=postgresql://deliveroo:deliveroo@localhost:5432/deliveroo_dev
flask db upgrade
python -m scripts.seed
flask run

# Exercise endpoints with curl
# (replace TOKEN with actual JWT from login)

# Login
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@deliveroo.dev","password":"password123"}'

# Get parcel detail
curl http://localhost:5000/parcels/1 \
  -H "Authorization: Bearer TOKEN"

# Change destination
curl -X PATCH http://localhost:5000/parcels/1/destination \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"destination":"Lavington, Nairobi"}'

# Cancel parcel
curl -X PATCH http://localhost:5000/parcels/1/cancel \
  -H "Authorization: Bearer TOKEN"

# Get status history
curl http://localhost:5000/parcels/1/status-history \
  -H "Authorization: Bearer TOKEN"
```
