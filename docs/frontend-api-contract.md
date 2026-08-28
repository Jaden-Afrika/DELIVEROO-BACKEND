# Frontend API Contract

Based on inspection of `https://github.com/Jaden-Afrika/DELIVEROO-FRONTEND` source code.

## Base URL

- Env var: `VITE_API_URL` (default `http://localhost:5000`)
- No `/api` prefix — endpoints are at root level

## Auth

- Token stored in localStorage as `deliveroo-token`
- User object stored as `deliveroo-user`
- Header: `Authorization: Bearer <token>`
- Response uses `access_token` (preferred) or `token` key

## Endpoints

### Auth
| Method | Path | Request | Response |
|--------|------|---------|----------|
| POST | `/auth/signup` | `{name, email, password, confirmPassword}` | `{access_token, user: {id, name, email, role}}` |
| POST | `/auth/login` | `{email, password}` | `{access_token, user: {id, name, email, role}}` |
| POST | `/auth/logout` | — | `{message}` |
| GET | `/auth/me` | — | `{user: {id, name, email, role}}` |

### Parcels
| Method | Path | Request | Response |
|--------|------|---------|----------|
| GET | `/parcels/me` | — | `[parcel object]` |
| POST | `/parcels` | `{pickupLocation, destination, weightCategory, distanceKm, description?}` | parcel object |
| GET | `/parcels/<id>` | — | parcel object (detail) |
| PATCH | `/parcels/<id>/destination` | `{destination}` | parcel object |
| PATCH | `/parcels/<id>/cancel` | — | parcel object |
| GET | `/parcels/<id>/status-history` | — | `[{id, status, changedByUserId, notes, createdAt}]` |
| GET | `/parcels/<id>/tracking` | — | 501 Not Implemented |

### Admin
| Method | Path | Request | Response |
|--------|------|---------|----------|
| GET | `/admin/parcels` | — | `[parcel object]` |
| PATCH | `/admin/parcels/<id>/status` | `{status: pending/in_transit/delivered}` | parcel object |
| PATCH | `/admin/parcels/<id>/location` | `{currentLocation}` | parcel object |

## Parcel Object Shape

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
  "dateCreated": "2026-08-25T10:00:00+00:00",
  "cancelledAt": "2026-08-25T11:00:00+00:00"
}
```

### Field Notes

| Field | Type | Notes |
|-------|------|-------|
| `id` | integer | Parcel primary key |
| `trackingNumber` | string | Format: `DRV-{8 hex chars}` |
| `pickupLocation` | string | Free-text address |
| `destination` | string | Free-text address, mutable |
| `weightCategory` | enum | `light`, `medium`, `heavy` |
| `weight` | string | Human-readable label (e.g. `"Light (0 - 2kg)"`) |
| `distanceKm` | float | Recalculated on destination change |
| `estimatedTravelTime` | integer | Minutes, computed from distance (40 km/h avg) |
| `price` | float | Recalculated on destination change |
| `currency` | string | Always `"KES"` |
| `status` | enum | `pending`, `assigned`, `in_transit`, `delivered`, `cancelled` |
| `currentLocation` | string | Free-text, set by admin or geocoding |
| `createdBy` | string | Owner user ID as string |
| `ownerId` | string | Owner user ID as string (duplicate of createdBy) |
| `ownerName` | string | Owner's `full_name` |
| `createdAt` | ISO-8601 | Parcel creation timestamp |
| `dateCreated` | ISO-8601 | Same as `createdAt` (frontend compatibility) |
| `cancelledAt` | ISO-8601 | Present only after cancellation |

## GET `/parcels/<id>` — Detail Response

**Authorization:** Owner or admin.

**Success (200):** Full parcel object as above.

**Errors:**
- 401: Unauthenticated
- 404: `{"error": {"code": "PARCEL_NOT_FOUND", "message": "Parcel not found."}}`

## PATCH `/parcels/<id>/destination` — Update Destination

**Authorization:** Owner or admin.

**Request:**
```json
{"destination": "Lavington, Nairobi"}
```

**Server-side rules:**
- Destination must be non-empty, 1-255 characters
- Delivered parcels cannot be changed (409)
- Cancelled parcels cannot be changed (409)
- Pending/assigned/in_transit parcels can be changed
- Distance and price are recalculated via geocoding/routing services
- Same destination: no-op, returns parcel unchanged

**Success (200):** Full updated parcel object.

**Errors:**
- 401: Unauthenticated
- 404: `{"error": {"code": "PARCEL_NOT_FOUND", ...}}`
- 409: `{"error": {"code": "PARCEL_DELIVERED", ...}}` or `{"error": {"code": "PARCEL_CANCELLED", ...}}`
- 422: `{"error": {"code": "VALIDATION_ERROR", ...}}`
- 500: `{"error": {"code": "UPDATE_FAILED", ...}}`

## PATCH `/parcels/<id>/cancel` — Cancel Parcel

**Authorization:** Owner or admin.

**Request body:** Empty (no body required).

**Server-side rules:**
- Delivered parcels cannot be cancelled (409)
- Already-cancelled parcels cannot be cancelled again (409)
- Pending/assigned/in_transit parcels can be cancelled
- Soft cancel: sets `status` to `cancelled`, records `cancelled_at`
- Creates `parcel_status_history` record atomically

**Success (200):** Full updated parcel with `status: "cancelled"` and `cancelledAt` field.

**Errors:**
- 401: Unauthenticated
- 404: `{"error": {"code": "PARCEL_NOT_FOUND", ...}}`
- 409: `{"error": {"code": "PARCEL_DELIVERED", ...}}` or `{"error": {"code": "PARCEL_CANCELLED", ...}}`

## Status History

```json
[
  {
    "id": 1,
    "status": "pending",
    "changedByUserId": 1,
    "notes": "Parcel created",
    "createdAt": "2026-08-25T10:00:00+00:00"
  }
]
```

Status history is created atomically with parcel creation and cancellation.

## Error Format

All errors use structured format:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message."
  }
}
```

The frontend also accepts flat `{"error": "message"}` format.

## Known Frontend Discrepancies

The frontend has two copies of parcel code (`src/` vs root `features/`) with conflicting field names:
- `weight` vs `weightCategory`
- `dateCreated` vs `createdAt`
- `createdBy` vs `ownerId`

The backend returns all fields to satisfy both versions.

The frontend's `ChangeDestinationForm` uses a synchronous Redux action (no API call). The `PATCH /parcels/<id>/destination` endpoint exists but is not currently called by the frontend.

`estimatedTravelTime` is computed client-side by `RouteMap` via OSM/OSRM. The backend also provides it but the frontend does not currently use it.

`currency` is hardcoded as `"KSh"` in frontend display code. The backend includes it in the response for completeness.

## Decisions / Open Questions

1. **Destination changes allowed for:** All non-delivered, non-cancelled statuses (pending, assigned, in_transit). Documented decision.
2. **Price recalculation on destination change:** Yes, distance and price are recalculated using geocoding/routing services. Documented decision.
3. **`estimatedTravelTime` unit:** Integer minutes, computed as `(distanceKm / 40) * 60` rounded. Documented decision.
4. **Cancellation method:** `PATCH` (not `DELETE`). Matches frontend contract. Documented decision.
5. **Non-owner access failures:** Return 404 (not 403) to avoid leaking parcel existence. Documented decision.
