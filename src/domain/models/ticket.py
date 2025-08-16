from datetime import datetime
from typing import Optional

class Ticket:
    def __init__(
        self,
        TicketID: Optional[int],
        EventDate: datetime,
        Price: float,
        EventName: str,
        Status: Optional[str],
        OwnerID: int
    ):
        self.TicketID = TicketID
        self.EventDate = EventDate
        self.Price = Price
        self.EventName = EventName
        self.Status = Status
        self.OwnerID = OwnerID