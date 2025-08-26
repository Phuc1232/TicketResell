from datetime import datetime
from typing import Optional

class Earning:
    def __init__(
        self,
        EarningID: Optional[int],
        UserID: int,
        TotalAmount: float,
        Date: datetime
    ):
        self.EarningID = EarningID
        self.UserID = UserID
        self.TotalAmount = TotalAmount
        self.Date = Date
