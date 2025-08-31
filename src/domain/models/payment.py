from datetime import datetime
from typing import Optional

class Payment:
    def __init__(
        self,
        PaymentID: Optional[int],
        Methods: str,
        Status: str,
        Paid_at: Optional[datetime],
        amount: float,
        UserID: int,
        Title: str,
        TransactionID: Optional[int],
        transaction_reference: Optional[str] = None
    ):
        self.PaymentID = PaymentID
        self.Methods = Methods
        self.Status = Status
        self.Paid_at = Paid_at
        self.amount = amount
        self.UserID = UserID
        self.Title = Title
        self.TransactionID = TransactionID
        self.transaction_reference = transaction_reference
