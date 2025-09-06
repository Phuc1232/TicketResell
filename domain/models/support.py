from datetime import datetime
from typing import Optional

class Support:
    def __init__(
        self,
        SupportID: Optional[int],
        UserID: int,
        Status: str,
        Create_at: datetime,
        Updated_at: Optional[datetime],
        Issue_des: Optional[str],
        Title: str,
        RecipientType: str,
        RecipientID: Optional[int]
    ):
        self.SupportID = SupportID
        self.UserID = UserID
        self.Status = Status
        self.Create_at = Create_at
        self.Updated_at = Updated_at
        self.Issue_des = Issue_des
        self.Title = Title
        self.RecipientType = RecipientType
        self.RecipientID = RecipientID
