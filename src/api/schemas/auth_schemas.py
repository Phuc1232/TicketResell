from marshmallow import Schema, fields, validate

class RegisterSchema(Schema):
    """Schema for user registration"""
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6, max=128))
    phone_number = fields.Str(required=True, validate=validate.Length(min=10, max=15))
    date_of_birth = fields.DateTime(required=True)

class LoginSchema(Schema):
    """Schema for user login"""
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=1))

class VerificationSchema(Schema):
    """Schema for account verification"""
    verification_code = fields.Str(required=True, validate=validate.Length(equal=6))

class ChangePasswordSchema(Schema):
    """Schema for changing password"""
    old_password = fields.Str(required=True, validate=validate.Length(min=1))
    new_password = fields.Str(required=True, validate=validate.Length(min=6, max=128))

class ResetPasswordSchema(Schema):
    """Schema for password reset request"""
    email = fields.Email(required=True)

class ConfirmResetSchema(Schema):
    """Schema for confirming password reset"""
    token = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate.Length(min=6, max=128))

class ResendVerificationSchema(Schema):
    """Schema for resending verification code"""
    pass

# Create schema instances
register_schema = RegisterSchema()
login_schema = LoginSchema()
verification_schema = VerificationSchema()
change_password_schema = ChangePasswordSchema()
reset_password_schema = ResetPasswordSchema()
confirm_reset_schema = ConfirmResetSchema()
resend_verification_schema = ResendVerificationSchema()

