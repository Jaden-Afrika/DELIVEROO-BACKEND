# Architecture

## Module Boundaries

```
app.py → create_app() → registers blueprints, extensions, error handlers
app/extensions.py → singletons: db, migrate, jwt, cors
app/config.py → Config / TestConfig classes
app/errors.py → JSON error handlers

app/models/ → SQLAlchemy ORM models (one file per table)
app/schemas/ → Marshmallow serialization/deserialization
app/routes/ → Flask Blueprints with auth decorators
app/services/ → Business logic and provider interfaces
```

## Request Flow

1. Request hits Flask router
2. Blueprint route handler receives request
3. Auth decorators verify JWT, load user
4. Marshmallow schema validates input
5. Service layer executes business logic
6. SQLAlchemy models persist data
7. Response serialized through Marshmallow
8. JSON response returned

## Auth Flow

1. Client sends `Authorization: Bearer <token>` header
2. Flask-JWT-Extended validates the JWT
3. `get_jwt_identity()` returns user ID
4. `auth_required` / `admin_required` decorators load and verify the user

## Service Adapters

All external service integrations use abstract base classes with stub implementations:
- `GeocodingService` → `StubGeocodingService` (returns Nairobi coords)
- `RoutingService` → `StubRoutingService` (returns 10km/25min)
- `PaymentService` → `StubPaymentService` (returns completed)
- `NotificationService` → `StubNotificationService` (returns sent)
- `StorageService` → `LocalStorageService` (writes to local disk)

Production adapters should be plugged in via environment variables.
