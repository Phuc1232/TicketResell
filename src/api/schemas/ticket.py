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
    Status = fields.Str(required=False, validate=validate.OneOf(['Available', 'Sold', 'Reserved', 'Cancelled']),
                       error_messages={"validator_failed": "Status must be one of: Available, Sold, Reserved, Cancelled"})
    OwnerID = fields.Int(required=True, validate=validate.Range(min=1),
                        error_messages={"validator_failed": "Owner ID must be a positive integer"})

class TicketResponseSchema(Schema):
    TicketID = fields.Int(required=True)
    EventDate = fields.DateTime()
    Price = fields.Float()
    EventName = fields.Str()
    Status = fields.Str()
    OwnerID = fields.Int()

class TicketSearchSchema(Schema):
    event_name = fields.Str()
    min_price = fields.Float(validate=validate.Range(min=0))
    max_price = fields.Float(validate=validate.Range(min=0))
    date_from = fields.DateTime()
    date_to = fields.DateTime()
    status = fields.Str(validate=validate.OneOf(['Available', 'Sold', 'Reserved', 'Cancelled']))

class TicketReservationSchema(Schema):
    reservation_duration = fields.Int(required=True, validate=validate.Range(min=1, max=24), 
                                     error_messages={"required": "Reservation duration is required",
                                                    "validator_failed": "Duration must be between 1 and 24 hours"})
    buyer_message = fields.Str(validate=validate.Length(max=500))