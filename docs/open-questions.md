# Open Questions

## Resolved

1. **Endpoint prefix**: No `/api` prefix. Frontend calls `/auth/...`, `/parcels/...`, `/admin/...` directly at root.
2. **User display name**: Frontend expects `name` field. Backend model stores `full_name` and maps to `name` in `to_dict()`.
3. **Auth response**: Uses `access_token` (preferred) and `user` object.
4. **Parcel statuses**: `pending`, `in_transit`, `delivered`, `cancelled`. Admin can set `pending`, `in_transit`, `delivered` only.
5. **Weight categories**: `light`, `medium`, `heavy`.
6. **Auth storage**: localStorage keys `deliveroo-token` and `deliveroo-user`.
7. **CORS origin**: `http://localhost:5173` (from frontend `.env.example`).

## Unresolved

1. **Two parcel field name sets**: Frontend has `src/` and root `features/` copies with different field names. Which is the active version?
2. **Owner identification**: `CancelDeliveryButton` checks `ownerId`, `ChangeDestinationForm` checks `createdBy`. Which is authoritative?
3. **Parcel weight_kg**: ERD specifies optional `weight_kg` field. Frontend only sends `weightCategory`. Should we support exact weight input?
4. **Destination editing**: Frontend has `ChangeDestinationForm` but no API path was found. Is `PATCH /parcels/<id>/destination` correct?
5. **Payment integration**: No frontend payment flow was found. Should payments be integrated at the parcel creation or delivery completion stage?
6. **Tracking**: No frontend tracking UI was found. What tracking granularity is expected?
7. **Neon deployment**: Build plan mentions Neon. Is this still the target Postgres provider?
8. **Admin seed policy**: Should dev admin be auto-seeded or require manual creation?
9. **driver-management routes**: Not in frontend contract. Include stubs or omit?
10. **StatusBadge label inconsistency**: Component shows "Completed" for `delivered`, test expects "Delivered". Which is correct?
