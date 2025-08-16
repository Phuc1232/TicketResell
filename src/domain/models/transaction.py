from datetime import datetime
from typing import Optional

class Transaction:
    def __init__(
        self,
        TransactionID: Optional[int],
        TicketID: int,
        BuyerID: int,
        SellerID: int,
        Amount: float,
        PaymentMethod: str,
        Status: str,
        PaymentTransactionID: Optional[str],
        CreatedAt: datetime,
        UpdatedAt: Optional[datetime]
    ):
        self.TransactionID = TransactionID
        self.TicketID = TicketID
        self.BuyerID = BuyerID
        self.SellerID = SellerID
        self.Amount = Amount
        self.PaymentMethod = PaymentMethod
        self.Status = Status
        self.PaymentTransactionID = PaymentTransactionID
        self.CreatedAt = CreatedAt
        self.UpdatedAt = UpdatedAt
