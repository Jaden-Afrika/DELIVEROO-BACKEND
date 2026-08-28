# Open questions

## Mapping-provider scope decision

The backend deliberately uses OpenStreetMap's Nominatim for geocoding and OSRM
for routing instead of Google Maps. This removes the server-side Google Maps API
key and associated usage costs. Nominatim requests are limited to one per second;
if demand outgrows the public-service policy, the next step is to use a hosted or
self-hosted OpenStreetMap-compatible provider rather than reintroducing Google.
