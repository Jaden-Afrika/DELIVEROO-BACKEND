# Batch 2 — apply on top of your existing `complete-backend` branch

You're already on the branch with the first 4 patches applied (92 -> wait,
85 -> now 92 passed after this batch). Apply these two on top of it directly
— no need to check out anything new.

```bash
git am /path/to/deliveroo-backend-patches-batch2/*.patch
```

## What's in this batch

| Patch | What it does |
|---|---|
| `0005` | Real Google Maps geocoding and routing providers (was: fixed stub coordinates and a flat 10km/25min for every parcel, everywhere) |
| `0006` | Updates `docs/frontend-api-contract.md` and `docs/open-questions.md` to match what the API actually returns now, and records payments/driver-assignment as deliberately out of scope for the MVP |

Verified against a clean checkout of your branch at the point after patch `0004` — applies cleanly, 92/92 tests pass.

## To actually use the Google providers

They default to the stubs, so nothing changes until you opt in:

```bash
# .env
GEOCODING_PROVIDER=google
ROUTING_PROVIDER=google
GOOGLE_MAPS_API_KEY=your-server-side-key
```

That key needs the **Geocoding API** and **Directions API** enabled, and should be **IP-restricted** (server-side use) — it's a different key from the frontend's `VITE_GOOGLE_MAPS_API_KEY`, which is browser-restricted for map rendering.

## Still open after this batch

- PR #1 on GitHub still needs to be manually closed (superseded — I can't do this for you, no GitHub write access).
- Your local `afrika-parcels` branch still has that unpushed `b6493cb` commit — worth a look to see if there's anything in it not already covered here, since I can't see its contents from here (it's local-only, never pushed).
- Frontend still needs to consume `pickupLatitude`/`pickupLongitude`/`destinationLatitude`/`destinationLongitude` for the actual map component — that's frontend work, not covered by these backend patches.
- Real SMTP credentials, if you want live email delivery rather than console-logged notifications.
