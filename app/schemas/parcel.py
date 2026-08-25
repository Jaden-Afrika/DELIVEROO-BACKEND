from marshmallow import Schema, fields, validate


class CreateParcelRequestSchema(Schema):
    pickupLocation = fields.String(required=True, validate=validate.Length(min=1, max=255))
    destination = fields.String(required=True, validate=validate.Length(min=1, max=255))
    weightCategory = fields.String(
        required=True, validate=validate.OneOf(["light", "medium", "heavy"])
    )
    distanceKm = fields.Float(required=True, validate=validate.Range(min=0.1))
    description = fields.String(load_default=None)


class ParcelResponseSchema(Schema):
    id = fields.Integer()
    trackingNumber = fields.String()
    pickupLocation = fields.String()
    destination = fields.String()
    weightCategory = fields.String()
    weight = fields.String()
    distanceKm = fields.Float()
    price = fields.Float()
    status = fields.String()
    currentLocation = fields.String()
    createdBy = fields.String()
    ownerId = fields.String()
    ownerName = fields.String()
    createdAt = fields.DateTime()
    dateCreated = fields.DateTime()


class UpdateDestinationRequestSchema(Schema):
    destination = fields.String(required=True, validate=validate.Length(min=1, max=255))


class AdminUpdateStatusRequestSchema(Schema):
    status = fields.String(
        required=True, validate=validate.OneOf(["pending", "in_transit", "delivered"])
    )


class AdminUpdateLocationRequestSchema(Schema):
    currentLocation = fields.String(required=True, validate=validate.Length(min=1, max=255))


create_parcel_request = CreateParcelRequestSchema()
parcel_response = ParcelResponseSchema()
parcels_response = ParcelResponseSchema(many=True)
update_destination_request = UpdateDestinationRequestSchema()
admin_update_status_request = AdminUpdateStatusRequestSchema()
admin_update_location_request = AdminUpdateLocationRequestSchema()
