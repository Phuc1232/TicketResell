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
    
    def initiate_transaction(self, ticket_id: int, buyer_id: int, amount: float, payment_method: str, reserve_ticket: bool = False) -> Transaction:
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # Validate ticket exists and is available
            ticket = self.ticket_repository.get_by_id(ticket_id)
            if not ticket:
                raise ValueError("Ticket not found")
            
            # Kiểm tra trạng thái vé - chỉ cho phép nếu Available hoặc Reserved (trong trường hợp retry)
            if ticket.Status not in ["Available", "Reserved"]:
                raise ValueError(f"Ticket is not available for purchase. Current status: {ticket.Status}")
            
            # Validate buyer exists
            buyer = self.user_repository.get_by_id(buyer_id)
            if not buyer:
                raise ValueError("Buyer not found")
            
            # Validate seller exists
            seller = self.user_repository.get_by_id(ticket.OwnerID)
            if not seller:
                raise ValueError("Seller not found")
            
            # Prevent self-purchase
            if ticket.OwnerID == buyer_id:
                raise ValueError("Cannot purchase your own ticket")

            # Atomic operation: Reserve ticket and create transaction
            if reserve_ticket and ticket.Status == "Available":
                ticket.Status = "Reserved"
                self.ticket_repository.update(ticket)
                logger.info(f"Ticket {ticket_id} reserved for buyer {buyer_id}")

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
            
            created_transaction = self.transaction_repository.add(transaction)
            logger.info(f"Transaction {created_transaction.TransactionID} initiated for ticket {ticket_id}")
            
            return created_transaction
            
        except Exception as e:
            logger.error(f"Error initiating transaction for ticket {ticket_id}: {str(e)}")
            # Rollback ticket reservation if it was reserved
            if reserve_ticket:
                try:
                    ticket = self.ticket_repository.get_by_id(ticket_id)
                    if ticket and ticket.Status == "Reserved":
                        ticket.Status = "Available"
                        self.ticket_repository.update(ticket)
                        logger.info(f"Rolled back ticket {ticket_id} reservation due to error")
                except Exception as rollback_error:
                    logger.error(f"Error rolling back ticket reservation: {rollback_error}")
            raise
    
    def process_transaction_callback(self, transaction_id: int, status: str, payment_transaction_id: str = None) -> Transaction:
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            transaction = self.transaction_repository.get_by_id(transaction_id)
            if not transaction:
                raise ValueError("Transaction not found")
            
            logger.info(f"Processing transaction callback for {transaction_id}: {status}")
            
            # Prevent duplicate processing
            if transaction.Status == status:
                logger.warning(f"Transaction {transaction_id} already has status {status}")
                return transaction
            
            # Update transaction status
            old_status = transaction.Status
            transaction.Status = status
            if payment_transaction_id:
                transaction.PaymentTransactionID = payment_transaction_id
            transaction.UpdatedAt = datetime.now()
            
            # Atomic operation: Update transaction and ticket status together
            if status == "success":
                # Nếu thanh toán thành công, cập nhật trạng thái vé thành "Sold"
                ticket = self.ticket_repository.get_by_id(transaction.TicketID)
                if not ticket:
                    raise ValueError(f"Ticket {transaction.TicketID} not found")
                
                if ticket.Status not in ["Reserved", "Available"]:
                    raise ValueError(f"Cannot complete transaction - ticket status is {ticket.Status}")
                
                ticket.Status = "Sold"
                self.ticket_repository.update(ticket)
                logger.info(f"Ticket {transaction.TicketID} marked as sold")
                
            elif status == "failed":
                # Nếu thanh toán thất bại, rollback trạng thái vé về "Available"
                ticket = self.ticket_repository.get_by_id(transaction.TicketID)
                if ticket and ticket.Status == "Reserved":
                    ticket.Status = "Available"
                    self.ticket_repository.update(ticket)
                    logger.info(f"Ticket {transaction.TicketID} released back to available")
            
            # Update transaction record
            updated_transaction = self.transaction_repository.update(transaction)
            logger.info(f"Transaction {transaction_id} updated from {old_status} to {status}")
            
            return updated_transaction
            
        except Exception as e:
            logger.error(f"Error processing transaction callback for {transaction_id}: {str(e)}")
            # In case of error, try to rollback any partial changes
            try:
                if status == "success":
                    # If we were trying to mark as success but failed, ensure ticket is not left in inconsistent state
                    ticket = self.ticket_repository.get_by_id(transaction.TicketID)
                    if ticket and ticket.Status == "Sold":
                        ticket.Status = "Reserved"  # Rollback to reserved state
                        self.ticket_repository.update(ticket)
                        logger.info(f"Rolled back ticket {transaction.TicketID} from Sold to Reserved due to error")
            except Exception as rollback_error:
                logger.error(f"Error during rollback: {rollback_error}")
            raise
    
    def get_transaction_by_id(self, transaction_id: int) -> Optional[Transaction]:
        return self.transaction_repository.get_by_id(transaction_id)
    
    def get_transactions_by_user(self, user_id: int) -> List[Transaction]:
        return self.transaction_repository.get_by_user_id(user_id)
    
    def get_transactions_by_ticket(self, ticket_id: int) -> List[Transaction]:
        return self.transaction_repository.get_by_ticket_id(ticket_id)
    
    def list_transactions(self) -> List[Transaction]:
        return self.transaction_repository.list()
