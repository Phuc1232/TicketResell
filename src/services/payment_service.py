from typing import List, Optional
from domain.models.payment import Payment
from domain.models.ipayment_repository import IPaymentRepository
from domain.models.iuser_repository import IUserRepository
from domain.models.itransaction_repository import ITransactionRepository
from datetime import datetime

class PaymentService:
    def __init__(self, payment_repository: IPaymentRepository, user_repository: IUserRepository, transaction_repository: ITransactionRepository):
        self.payment_repository = payment_repository
        self.user_repository = user_repository
        self.transaction_repository = transaction_repository
    
    def create_payment(self, methods: str, amount: float, user_id: int, title: str, transaction_id: Optional[int] = None) -> Payment:
        # Validate user exists
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Validate transaction exists if provided
        if transaction_id:
            transaction = self.transaction_repository.get_by_id(transaction_id)
            if not transaction:
                raise ValueError("Transaction not found")
        
        # Create payment
        payment = Payment(
            PaymentID=None,
            Methods=methods,
            Status='pending',
            Paid_at=None,
            amount=amount,
            UserID=user_id,
            Title=title,
            TransactionID=transaction_id
        )
        
        return self.payment_repository.add(payment)
    
    def get_payment(self, payment_id: int) -> Optional[Payment]:
        return self.payment_repository.get_by_id(payment_id)
    
    def get_user_payments(self, user_id: int) -> List[Payment]:
        # Validate user exists
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        return self.payment_repository.get_by_user_id(user_id)
    
    def update_payment_status(self, payment_id: int, status: str) -> Optional[Payment]:
        payment = self.payment_repository.get_by_id(payment_id)
        if not payment:
            return None
        
        payment.Status = status
        if status == 'success':
            payment.Paid_at = datetime.now()
        
        return self.payment_repository.update(payment)
    
    def get_payments_by_status(self, status: str) -> List[Payment]:
        return self.payment_repository.get_by_status(status)
    
    def delete_payment(self, payment_id: int) -> bool:
        payment = self.payment_repository.get_by_id(payment_id)
        if not payment:
            return False
        
        return self.payment_repository.delete(payment_id)
