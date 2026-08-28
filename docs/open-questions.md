# Open Questions

## Resolved

1. **Endpoint prefix**: No `/api` prefix. Frontend calls `/auth/...`, `/parcels/...`, `/admin/...` directly at root.
2. **User display name**: Frontend expects `name` field. Backend model stores `full_name` and maps to `name` in `to_dict()`.
3. **Auth response**: Uses `access_token` (preferred) and `user` object.
4. **Parcel statuses**: `pending`, `assigned`, `in_transit`, `delivered`, `cancelled`. Admin can set `pending`, `assigned`, `in_transit`, `delivered`; `cancelled` only happens through the dedicated cancel endpoint (owner-only, with its own not-delivered/not-already-cancelled rules), never as an arbitrary admin status change.
5. **Weight categories**: `light`, `medium`, `heavy`.
6. **Auth storage**: localStorage keys `deliveroo-token` and `deliveroo-user`.
7. **CORS origin**: `http://localhost:5173` (from frontend `.env.example`).

## Unresolved

1. **Two parcel field name sets**: Frontend has `src/` and root `features/` copies with different field names. Which is the active version?
2. **Owner identification**: `CancelDeliveryButton` checks `ownerId`, `ChangeDestinationForm` checks `createdBy`. Which is authoritative?
3. **Parcel weight_kg**: ERD specifies optional `weight_kg` field. Frontend only sends `weightCategory`. Should we support exact weight input?
4. **Destination editing**: Frontend has `ChangeDestinationForm` but no API path was found. Is `PATCH /parcels/<id>/destination` correct?
6. **Neon deployment**: Build plan mentions Neon. Is this still the target Postgres provider?
7. **Admin seed policy**: Should dev admin be auto-seeded or require manual creation?
8. **StatusBadge label inconsistency**: Component shows "Completed" for `delivered`, test expects "Delivered". Which is correct?

## Deliberately out of scope for the MVP

These have model scaffolding (`Payment`, `Driver`, `Delivery`, `TrackingLocation`) already in place from the original ERD, but no endpoints or business logic, because they're not in the MVP feature list:

5. **Payment integration**: `PaymentService`/`StubPaymentService` exist but nothing in the MVP spec calls for collecting payment — parcels are quoted a price, not charged one. Left as scaffolding only. Revisit if/when a payment flow is actually specced.
9. **Driver assignment**: `Driver` and `Delivery` models exist, and `assigned` is now a valid parcel status, but there's no endpoint to actually assign a driver to a delivery — status changes are admin-driven, not driver-driven. Fine for the MVP's "admin changes status and location" requirement; would need real work if driver-facing features get added later.
10. **Tracking**: `GET /parcels/<id>/tracking` now returns real data (parcel status, coordinates, distance, ETA, last update) instead of 501, but it's a snapshot from the parcel + status history — not live GPS breadcrumbs from a driver's device. `TrackingLocation` model exists for that future case but nothing populates it yet. No frontend tracking UI was found either, so this may be ahead of what's actually being built against.
