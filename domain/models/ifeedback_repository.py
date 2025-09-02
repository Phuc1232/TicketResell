from abc import ABC, abstractmethod
from typing import List, Optional
from domain.models.feedback import Feedback, TicketFeedback

class IFeedbackRepository(ABC):
    @abstractmethod
    def add_user_feedback(self, feedback: Feedback) -> Feedback:
        pass
    
    @abstractmethod
    def add_ticket_feedback(self, feedback: TicketFeedback) -> TicketFeedback:
        pass
    
    @abstractmethod
    def get_user_feedback(self, user_id: int, limit: int = 20, offset: int = 0) -> List[Feedback]:
        pass
    
    @abstractmethod
    def get_ticket_feedback(self, ticket_id: int, limit: int = 20, offset: int = 0) -> List[TicketFeedback]:
        pass
    
    @abstractmethod
    def get_average_user_rating(self, user_id: int) -> float:
        pass
    
    @abstractmethod
    def get_average_ticket_rating(self, ticket_id: int) -> float:
        pass
    
    @abstractmethod
    def delete_user_feedback(self, feedback_id: int) -> bool:
        pass
    
    @abstractmethod
    def delete_ticket_feedback(self, feedback_id: int) -> bool:
        pass

    @abstractmethod
    def get_feedback_by_transaction(self, transaction_id: int, reviewer_id: int) -> Optional[Feedback]:
        pass

    @abstractmethod
    def get_feedback_as_buyer(self, user_id: int) -> List[Feedback]:
        pass

    @abstractmethod
    def get_feedback_as_seller(self, user_id: int) -> List[Feedback]:
        pass
