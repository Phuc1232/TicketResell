from datetime import datetime
from typing import Optional

class Message:
    def __init__(
        self,
        MessageID: Optional[int],
        SenderID: int,
        ReceiverID: int,
        Content: str,
        TicketID: Optional[int],
        IsRead: bool,
        SentAt: datetime,
        ReadAt: Optional[datetime]
    ):
        self.MessageID = MessageID
        self.SenderID = SenderID
        self.ReceiverID = ReceiverID
        self.Content = Content
        self.TicketID = TicketID
        self.IsRead = IsRead
        self.SentAt = SentAt
        self.ReadAt = ReadAt
