from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from api.schemas.ticket import TicketRequestSchema, TicketResponseSchema, TicketSearchSchema, TicketReservationSchema
from api.schemas.user import UserLoginSchema, UserRegisterSchema, UserResponseSchema, UserUpdateSchema, UserVerificationSchema, UserRatingSchema
spec = APISpec(
    title="TicketResell API",
    version="1.0.0",
    openapi_version="3.0.2",
    plugins=[FlaskPlugin(), MarshmallowPlugin()],
)
spec.components.security_scheme(
    "BearerAuth",
    {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT"
    }
)


# Schema Ticket
spec.components.schema("TicketRequest", schema=TicketRequestSchema)
spec.components.schema("TicketResponse", schema=TicketResponseSchema)
spec.components.schema("TicketSearch", schema=TicketSearchSchema)
spec.components.schema("TicketReservation", schema=TicketReservationSchema)

# Schema User
spec.components.schema("UserResponse",schema=UserResponseSchema)
spec.components.schema("UserLogin",schema=UserLoginSchema)
spec.components.schema("UserRegister",schema=UserRegisterSchema)
spec.components.schema("UserUpdate",schema=UserUpdateSchema)
spec.components.schema("UserVerification",schema=UserVerificationSchema)
spec.components.schema("UserRating",schema=UserRatingSchema)