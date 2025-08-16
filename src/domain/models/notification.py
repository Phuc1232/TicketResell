from datetime import datetime
from typing import Optional

class Notification:
    def __init__(
        self,
        NotificationID: Optional[int],
        UserID: int,
        Title: str,
        Content: str,
        Type: str,
        IsRead: bool,
        CreatedAt: datetime,
        ReadAt: Optional[datetime]
    ):
        self.NotificationID = NotificationID
        self.UserID = UserID
        self.Title = Title
        self.Content = Content
        self.Type = Type
        self.IsRead = IsRead
        self.CreatedAt = CreatedAt
        self.ReadAt = ReadAt
