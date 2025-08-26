from datetime import datetime
from typing import Optional

class Feedback:
    def __init__(
        self,
        FeedbackID: Optional[int],
        ReviewerID: int,
        TargetUserID: int,
        Rating: float,
        Comment: Optional[str],
        TransactionID: Optional[int],
        CreatedAt: datetime
    ):
        self.FeedbackID = FeedbackID
        self.ReviewerID = ReviewerID
        self.TargetUserID = TargetUserID
        self.Rating = Rating
        self.Comment = Comment
        self.TransactionID = TransactionID
        self.CreatedAt = CreatedAt

class TicketFeedback:
    def __init__(
        self,
        FeedbackID: Optional[int],
        ReviewerID: int,
        TicketID: int,
        Rating: float,
        Comment: Optional[str],
        CreatedAt: datetime
    ):
        self.FeedbackID = FeedbackID
        self.ReviewerID = ReviewerID
        self.TicketID = TicketID
        self.Rating = Rating
        self.Comment = Comment
        self.CreatedAt = CreatedAt
