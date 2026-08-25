from marshmallow import Schema, fields, validate


class SignupRequestSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=255))
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=6))
    confirmPassword = fields.String(required=True)


class LoginRequestSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)


class UserResponseSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    email = fields.String()
    role = fields.String()
    created_at = fields.DateTime()


class AuthResponseSchema(Schema):
    access_token = fields.String()
    user = fields.Nested(UserResponseSchema)


signup_request = SignupRequestSchema()
login_request = LoginRequestSchema()
auth_response = AuthResponseSchema()
