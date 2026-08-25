# Database Schema

## Tables

### users
| Column | Type | Constraints |
|--------|------|-------------|
| id | integer PK | auto |
| full_name | varchar(255) | NOT NULL |
| email | varchar(255) | NOT NULL, UNIQUE, INDEX |
| password_hash | varchar(255) | NOT NULL |
| phone_number | varchar(50) | nullable |
| role | enum(user, admin) | NOT NULL, default user |
| is_active | boolean | NOT NULL, default true |
| created_at | timestamptz | NOT NULL |
| updated_at | timestamptz | NOT NULL |

### drivers
| Column | Type | Constraints |
|--------|------|-------------|
| id | integer PK | |
| user_id | integer FK→users | NOT NULL, UNIQUE |
| vehicle_type | varchar(100) | NOT NULL |
| vehicle_registration | varchar(100) | NOT NULL |
| licence_number | varchar(100) | NOT NULL |
| enum availability_status | available/assigned/offline/suspended | NOT NULL |
| is_verified | boolean | NOT NULL, default false |
| created_at | timestamptz | NOT NULL |
| updated_at | timestamptz | NOT NULL |

### addresses
| Column | Type | Constraints |
|--------|------|-------------|
| id | integer PK | |
| user_id | integer FK→users | NOT NULL |
| label | varchar(100) | nullable |
| recipient_name | varchar(255) | NOT NULL |
| recipient_phone | varchar(50) | NOT NULL |
| address_line_1 | varchar(255) | NOT NULL |
| address_line_2 | varchar(255) | nullable |
| city | varchar(100) | NOT NULL |
| region_or_state | varchar(100) | NOT NULL |
| country | varchar(100) | NOT NULL |
| postal_code | varchar(20) | nullable |
| latitude | numeric(9,6) | NOT NULL |
| longitude | numeric(9,6) | NOT NULL |
| created_at | timestamptz | NOT NULL |
| updated_at | timestamptz | NOT NULL |

### pricing_rules
| Column | Type | Constraints |
|--------|------|-------------|
| id | integer PK | |
| weight_category | enum(light, medium, heavy) | NOT NULL |
| base_fee | numeric(12,2) | NOT NULL |
| per_km_rate | numeric(12,2) | NOT NULL |
| currency | varchar(3) | NOT NULL |
| is_active | boolean | NOT NULL, default true |
| effective_from | timestamptz | NOT NULL |
| expires_at | timestamptz | nullable |
| created_at | timestamptz | NOT NULL |

### parcels
| Column | Type | Constraints |
|--------|------|-------------|
| id | integer PK | |
| tracking_number | varchar(100) | NOT NULL, UNIQUE, INDEX |
| customer_id | integer FK→users | NOT NULL |
| pickup_address_id | integer FK→addresses | nullable |
| destination_address_id | integer FK→addresses | nullable |
| weight_category | enum(light, medium, heavy) | NOT NULL |
| weight_kg | numeric(10,3) | nullable |
| description | text | nullable |
| pickup_location | varchar(255) | NOT NULL |
| destination | varchar(255) | NOT NULL |
| distance_km | numeric(10,2) | NOT NULL |
| quoted_price | numeric(12,2) | NOT NULL |
| final_price | numeric(12,2) | nullable |
| currency | varchar(3) | NOT NULL |
| status | enum(pending, assigned, in_transit, delivered, cancelled) | NOT NULL, default pending |
| current_location | varchar(255) | nullable |
| created_at | timestamptz | NOT NULL |
| updated_at | timestamptz | NOT NULL |
| cancelled_at | timestamptz | nullable |
| delivered_at | timestamptz | nullable |

### parcel_status_history
| Column | Type | Constraints |
|--------|------|-------------|
| id | integer PK | |
| parcel_id | integer FK→parcels | NOT NULL |
| status | parcel-status enum | NOT NULL |
| changed_by_user_id | integer FK→users | nullable |
| notes | text | nullable |
| created_at | timestamptz | NOT NULL |

### deliveries
| Column | Type | Constraints |
|--------|------|-------------|
| id | integer PK | |
| parcel_id | integer FK→parcels | NOT NULL, UNIQUE |
| driver_id | integer FK→drivers | nullable |
| assigned_by_user_id | integer FK→users | nullable |
| assigned_at | timestamptz | nullable |
| picked_up_at | timestamptz | nullable |
| delivered_at | timestamptz | nullable |
| delivery_notes | text | nullable |
| proof_of_delivery_url | varchar(1000) | nullable |
| created_at | timestamptz | NOT NULL |
| updated_at | timestamptz | NOT NULL |

### tracking_locations
| Column | Type | Constraints |
|--------|------|-------------|
| id | integer PK | |
| delivery_id | integer FK→deliveries | NOT NULL |
| latitude | numeric(9,6) | NOT NULL |
| longitude | numeric(9,6) | NOT NULL |
| location_text | varchar(255) | nullable |
| recorded_at | timestamptz | NOT NULL |

### payments
| Column | Type | Constraints |
|--------|------|-------------|
| id | integer PK | |
| parcel_id | integer FK→parcels | NOT NULL |
| customer_id | integer FK→users | NOT NULL |
| amount | numeric(12,2) | NOT NULL |
| currency | varchar(3) | NOT NULL |
| payment_method | varchar(50) | NOT NULL |
| provider | varchar(100) | nullable |
| provider_transaction_id | varchar(255) | nullable, UNIQUE |
| payment_status | enum(pending, completed, failed, refunded) | NOT NULL |
| paid_at | timestamptz | nullable |
| created_at | timestamptz | NOT NULL |
| updated_at | timestamptz | NOT NULL |

### notifications
| Column | Type | Constraints |
|--------|------|-------------|
| id | integer PK | |
| user_id | integer FK→users | NOT NULL |
| parcel_id | integer FK→parcels | nullable |
| type | varchar(100) | NOT NULL |
| title | varchar(255) | NOT NULL |
| message | text | NOT NULL |
| read_at | timestamptz | nullable |
| created_at | timestamptz | NOT NULL |

## Enum Values

- **UserRole**: user, admin
- **DriverAvailabilityStatus**: available, assigned, offline, suspended
- **ParcelStatus**: pending, assigned, in_transit, delivered, cancelled
- **WeightCategory**: light, medium, heavy
- **PaymentStatus**: pending, completed, failed, refunded

## Frontend Compatibility Notes

The Parcel model stores both normalized fields (`pickup_location`, `destination`, `weight_category`) and the flat denormalized strings (`pickup_location`, `destination`) that the frontend expects. The `to_dict()` method returns camelCase keys matching the frontend contract:
- `pickupLocation` ← `pickup_location`
- `destination` ← `destination`
- `weightCategory` ← `weight_category`
- `weight` ← computed display label
- `price` ← `quoted_price`
- `createdBy` / `ownerId` ← `customer_id`
- `ownerName` ← joined from `users.full_name`
- `createdAt` / `dateCreated` ← `created_at`
