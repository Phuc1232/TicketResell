from typing import List, Optional
from domain.models.feedback import Feedback, TicketFeedback
from domain.models.ifeedback_repository import IFeedbackRepository
from domain.models.iuser_repository import IUserRepository
from domain.models.itticket_repository import ITicketRepository
from domain.models.itransaction_repository import ITransactionRepository
from datetime import datetime

class FeedbackService:
    def __init__(self, feedback_repository: IFeedbackRepository, user_repository: IUserRepository, 
                 ticket_repository: ITicketRepository, transaction_repository: ITransactionRepository):
        self.feedback_repository = feedback_repository
        self.user_repository = user_repository
        self.ticket_repository = ticket_repository
        self.transaction_repository = transaction_repository
    
    def submit_user_feedback(self, reviewer_id: int, target_user_id: int, rating: float, 
                           comment: Optional[str] = None, transaction_id: Optional[int] = None) -> Feedback:
        # Validate reviewer exists
        reviewer = self.user_repository.get_by_id(reviewer_id)
        if not reviewer:
            raise ValueError("Reviewer not found")
        
        # Validate target user exists
        target_user = self.user_repository.get_by_id(target_user_id)
        if not target_user:
            raise ValueError("Target user not found")
        
        # Validate rating range
        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5")
        
        # Validate transaction exists if provided
        if transaction_id:
            transaction = self.transaction_repository.get_by_id(transaction_id)
            if not transaction:
                raise ValueError("Transaction not found")
        
        # Create feedback
        feedback = Feedback(
            FeedbackID=None,
            ReviewerID=reviewer_id,
            TargetUserID=target_user_id,
            Rating=rating,
            Comment=comment,
            TransactionID=transaction_id,
            CreatedAt=datetime.now()
        )
        
        return self.feedback_repository.add_user_feedback(feedback)
    
    def submit_ticket_feedback(self, reviewer_id: int, ticket_id: int, rating: float, 
                             comment: Optional[str] = None) -> TicketFeedback:
        # Validate reviewer exists
        reviewer = self.user_repository.get_by_id(reviewer_id)
        if not reviewer:
            raise ValueError("Reviewer not found")
        
        # Validate ticket exists
        ticket = self.ticket_repository.get_by_id(ticket_id)
        if not ticket:
            raise ValueError("Ticket not found")
        
        # Validate rating range
        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5")
        
        # Create ticket feedback
        feedback = TicketFeedback(
            FeedbackID=None,
            ReviewerID=reviewer_id,
            TicketID=ticket_id,
            Rating=rating,
            Comment=comment,
            CreatedAt=datetime.now()
        )
        
        return self.feedback_repository.add_ticket_feedback(feedback)
    
    def get_user_feedback(self, user_id: int, limit: int = 20, offset: int = 0) -> List[Feedback]:
        # Validate user exists
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        return self.feedback_repository.get_user_feedback(user_id, limit, offset)
    
    def get_ticket_feedback(self, ticket_id: int, limit: int = 20, offset: int = 0) -> List[TicketFeedback]:
        # Validate ticket exists
        ticket = self.ticket_repository.get_by_id(ticket_id)
        if not ticket:
            raise ValueError("Ticket not found")
        
        return self.feedback_repository.get_ticket_feedback(ticket_id, limit, offset)
    
    def get_average_user_rating(self, user_id: int) -> float:
        # Validate user exists
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        return self.feedback_repository.get_average_user_rating(user_id)
    
    def get_average_ticket_rating(self, ticket_id: int) -> float:
        # Validate ticket exists
        ticket = self.ticket_repository.get_by_id(ticket_id)
        if not ticket:
            raise ValueError("Ticket not found")
        
        return self.feedback_repository.get_average_ticket_rating(ticket_id)
    
    def delete_user_feedback(self, feedback_id: int, user_id: int) -> bool:
        # Validate user exists
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Check if user owns the feedback
        feedback_list = self.feedback_repository.get_user_feedback(user_id, limit=1000, offset=0)
        feedback = next((f for f in feedback_list if f.FeedbackID == feedback_id), None)
        if not feedback or feedback.ReviewerID != user_id:
            raise ValueError("Feedback not found or access denied")
        
        return self.feedback_repository.delete_user_feedback(feedback_id)
    
    def delete_ticket_feedback(self, feedback_id: int, user_id: int) -> bool:
        # Validate user exists
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Check if user owns the feedback
        feedback_list = self.feedback_repository.get_ticket_feedback(0, limit=1000, offset=0)  # This needs to be improved
        feedback = next((f for f in feedback_list if f.FeedbackID == feedback_id), None)
        if not feedback or feedback.ReviewerID != user_id:
            raise ValueError("Feedback not found or access denied")
        
        return self.feedback_repository.delete_ticket_feedback(feedback_id)
