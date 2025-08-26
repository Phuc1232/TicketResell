# Dependency Injection Container

from infrastructure.repositories.ticket_repository import TicketRepository
from infrastructure.repositories.user_repository import UserRepository
from infrastructure.repositories.transaction_repository import TransactionRepository
from infrastructure.repositories.message_repository import MessageRepository

from infrastructure.repositories.feedback_repository import FeedbackRepository
from services.ticket_service import TicketService
from services.user_service import UserService
from services.transaction_service import TransactionService
from services.chat_service import ChatService

from services.feedback_service import FeedbackService

class DependencyContainer:
    def __init__(self):
        # Initialize repositories
        self.ticket_repository = TicketRepository()
        self.user_repository = UserRepository()
        self.transaction_repository = TransactionRepository()
        self.message_repository = MessageRepository()

        self.feedback_repository = FeedbackRepository()
        
        # Initialize services
        self.ticket_service = TicketService(self.ticket_repository)
        self.user_service = UserService(self.user_repository)
        self.transaction_service = TransactionService(
            self.transaction_repository, 
            self.ticket_repository, 
            self.user_repository
        )
        self.chat_service = ChatService(
            self.message_repository,
            self.user_repository,
            self.ticket_repository
        )

        self.feedback_service = FeedbackService(
            self.feedback_repository,
            self.user_repository,
            self.ticket_repository,
            self.transaction_repository
        )
    
    def get_ticket_service(self) -> TicketService:
        return self.ticket_service
    
    def get_user_service(self) -> UserService:
        return self.user_service
    
    def get_transaction_service(self) -> TransactionService:
        return self.transaction_service
    
    def get_chat_service(self) -> ChatService:
        return self.chat_service
    

    
    def get_feedback_service(self) -> FeedbackService:
        return self.feedback_service