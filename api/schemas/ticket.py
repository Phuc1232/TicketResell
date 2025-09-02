from marshmallow import Schema, fields, validate

class TicketRequestSchema(Schema):
    EventDate = fields.DateTime(required=True, 
                               error_messages={"required": "Event date is required",
                                              "invalid": "Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SSZ)"})
    Price = fields.Float(required=True, validate=validate.Range(min=0), 
                        error_messages={"required": "Price is required",
                                       "validator_failed": "Price must be greater than or equal to 0"})
    EventName = fields.Str(required=True, validate=validate.Length(min=1, max=100), 
                          error_messages={"required": "Event name is required", 
                                         "validator_failed": "Event name must be between 1 and 100 characters"})
    Status = fields.Str(required=True, validate=validate.OneOf(['Available', 'Sold', 'Reserved', 'Cancelled']),
                       error_messages={"required": "Status is required",
                                      "validator_failed": "Status must be one of: Available, Sold, Reserved, Cancelled"})
    PaymentMethod = fields.Str(required=True, validate=validate.OneOf(['Cash', 'Bank Transfer', 'Digital Wallet', 'Credit Card']),
                              error_messages={"required": "Payment method is required",
                                             "validator_failed": "Payment method must be one of: Cash, Bank Transfer, Digital Wallet, Credit Card"})
    ContactInfo = fields.Str(required=True, validate=validate.Length(min=1, max=200),
                            error_messages={"required": "Contact information is required",
                                           "validator_failed": "Contact information must be between 1 and 200 characters"})
    OwnerID = fields.Int(required=True, validate=validate.Range(min=1),
                        error_messages={"required": "Owner ID is required",
                                       "validator_failed": "Owner ID must be a positive integer"})

class TicketResponseSchema(Schema):
    TicketID = fields.Int(required=True)
    EventDate = fields.DateTime()
    Price = fields.Float()
    EventName = fields.Str()
    Status = fields.Str()
    PaymentMethod = fields.Str()
    ContactInfo = fields.Str()
    OwnerID = fields.Int()

class TicketSearchSchema(Schema):
    event_name = fields.Str()
    limit = fields.Int(validate=validate.Range(min=1, max=100))

class TicketRatingSchema(Schema):
    rating = fields.Float(required=True, validate=validate.Range(min=0, max=5),
                         error_messages={"required": "Rating is required",
                                        "validator_failed": "Rating must be between 0 and 5"})

class TicketReservationSchema(Schema):
    reservation_duration = fields.Int(required=True, validate=validate.Range(min=1, max=24), 
                                     error_messages={"required": "Reservation duration is required",
                                                    "validator_failed": "Duration must be between 1 and 24 hours"})
    buyer_message = fields.Str(validate=validate.Length(max=500))