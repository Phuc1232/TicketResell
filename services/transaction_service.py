from typing import List, Optional
from domain.models.transaction import Transaction
from domain.models.itransaction_repository import ITransactionRepository
from domain.models.itticket_repository import ITicketRepository
from domain.models.iuser_repository import IUserRepository
from datetime import datetime
import uuid

class TransactionService:
    def __init__(self, transaction_repository: ITransactionRepository, ticket_repository: ITicketRepository, user_repository: IUserRepository):
        self.transaction_repository = transaction_repository
        self.ticket_repository = ticket_repository
        self.user_repository = user_repository
    
    def initiate_transaction(self, ticket_id: int, buyer_id: int, amount: float, payment_method: str) -> Transaction:
        # Validate ticket exists and is available
        ticket = self.ticket_repository.get_by_id(ticket_id)
        if not ticket:
            raise ValueError("Ticket not found")
        
        if ticket.Status != "Available":
            raise ValueError("Ticket is not available for purchase")
        
        # Validate buyer exists
        buyer = self.user_repository.get_by_id(buyer_id)
        if not buyer:
            raise ValueError("Buyer not found")
        
        # Validate seller exists
        seller = self.user_repository.get_by_id(ticket.OwnerID)
        if not seller:
            raise ValueError("Seller not found")
        
        # Create transaction record
        transaction = Transaction(
            TransactionID=None,
            TicketID=ticket_id,
            BuyerID=buyer_id,
            SellerID=ticket.OwnerID,
            Amount=amount,
            PaymentMethod=payment_method,
            Status="pending",
            PaymentTransactionID=str(uuid.uuid4()),
            CreatedAt=datetime.now(),
            UpdatedAt=None
        )
        
        return self.transaction_repository.add(transaction)
    
    def process_transaction_callback(self, transaction_id: int, status: str, payment_transaction_id: str = None) -> Transaction:
        transaction = self.transaction_repository.get_by_id(transaction_id)
        if not transaction:
            raise ValueError("Transaction not found")
        
        transaction.Status = status
        if payment_transaction_id:
            transaction.PaymentTransactionID = payment_transaction_id
        transaction.UpdatedAt = datetime.now()
        
        # If transaction is successful, update ticket status
        if status == "success":
            ticket = self.ticket_repository.get_by_id(transaction.TicketID)
            if ticket:
                ticket.Status = "Sold"
                self.ticket_repository.update(ticket)
        
        return self.transaction_repository.update(transaction)
    
    def get_transaction_by_id(self, transaction_id: int) -> Optional[Transaction]:
        return self.transaction_repository.get_by_id(transaction_id)
    
    def get_transactions_by_user(self, user_id: int) -> List[Transaction]:
        return self.transaction_repository.get_by_user_id(user_id)
    
    def get_transactions_by_ticket(self, ticket_id: int) -> List[Transaction]:
        return self.transaction_repository.get_by_ticket_id(ticket_id)
    
    def list_transactions(self) -> List[Transaction]:
        return self.transaction_repository.list()
