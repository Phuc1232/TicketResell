from marshmallow import Schema, fields, validate

class UserRegisterSchema(Schema):
    phone_number = fields.Str(required=True, validate=validate.Length(min=10, max=15))
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    status = fields.Str(required=False, validate=validate.OneOf(['active', 'inactive', 'suspended']), load_default='active')
    password = fields.Str(required=True, validate=validate.Length(min=6))
    email = fields.Email(required=True)
    date_of_birth = fields.Date(required=True)
    role_id = fields.Int(required=False, validate=validate.OneOf([1, 2, 3, 4]))  # Optional, auto-assigned

class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class UserUpdateSchema(Schema):
    phone_number = fields.Str(validate=validate.Length(min=10, max=15))
    username = fields.Str(validate=validate.Length(min=3, max=50))
    status = fields.Str(validate=validate.OneOf(['active', 'inactive', 'suspended']))
    date_of_birth = fields.Date()

class UserResponseSchema(Schema):
    id = fields.Int()
    phone_number = fields.Str()
    username = fields.Str()
    status = fields.Str()
    email = fields.Email()
    date_of_birth = fields.Date()
    create_date = fields.DateTime()
    role_id = fields.Int()

class UserVerificationSchema(Schema):
    verification_code = fields.Str(required=True, validate=validate.Length(equal=6))
    verification_type = fields.Str(required=True, validate=validate.OneOf(['email', 'phone']))

class UserRatingSchema(Schema):
    rating = fields.Float(required=True, validate=validate.Range(min=1, max=5))
    comment = fields.Str(validate=validate.Length(max=500))
    transaction_id = fields.Int(required=True)
