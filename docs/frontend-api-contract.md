# Frontend API contract

## Address coordinates and route estimates

The backend geocodes parcel pickup and destination addresses with OpenStreetMap's
Nominatim service. It calculates driving distance and estimated duration with the
public OSRM routing service. These enrichments are best-effort: parcel creation
and destination updates still succeed if either public service is unavailable or
cannot find a result.

No Google Maps server-side API key is needed by this backend. Clients should
continue to treat returned coordinates and route estimates as optional fields.
