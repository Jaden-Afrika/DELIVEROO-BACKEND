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
  "price": 600.0,
  "status": "pending",
  "currentLocation": "Westlands, Nairobi",
  "createdBy": "1",
  "ownerId": "1",
  "ownerName": "Test User",
  "createdAt": "2026-08-25T10:00:00+00:00",
  "dateCreated": "2026-08-25T10:00:00+00:00"
}
```

## Known Frontend Discrepancies

The frontend has two copies of parcel code (`src/` vs root `features/`) with conflicting field names:
- `weight` vs `weightCategory`
- `dateCreated` vs `createdAt`
- `createdBy` vs `ownerId`

The backend returns all fields to satisfy both versions.
