from typing import List, Optional, Dict, Any
from domain.models.payment import Payment
from domain.models.ipayment_repository import IPaymentRepository
from domain.models.iuser_repository import IUserRepository
from domain.models.itransaction_repository import ITransactionRepository
from datetime import datetime, timedelta
import uuid
import logging

logger = logging.getLogger(__name__)

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

    def process_payment(self, payment_id: int, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process payment through payment gateway

        Args:
            payment_id: ID of the payment to process
            payment_data: Additional payment data from gateway

        Returns:
            Dict with payment result
        """
        payment = self.payment_repository.get_by_id(payment_id)
        if not payment:
            raise ValueError("Payment not found")

        if payment.Status != 'pending':
            raise ValueError(f"Payment is already {payment.Status}")

        try:
            # Simulate payment processing based on method
            result = self._process_payment_by_method(payment, payment_data)

            # Update payment status
            payment.Status = result['status']
            if result['status'] == 'success':
                payment.Paid_at = datetime.now()

            updated_payment = self.payment_repository.update(payment)

            logger.info(f"Payment {payment_id} processed with status: {result['status']}")

            return {
                'payment_id': payment_id,
                'status': result['status'],
                'message': result['message'],
                'transaction_reference': result.get('transaction_reference'),
                'payment': updated_payment
            }

        except Exception as e:
            logger.error(f"Payment processing failed for payment {payment_id}: {e}")
            payment.Status = 'failed'
            self.payment_repository.update(payment)
            raise ValueError(f"Payment processing failed: {e}")

    def _process_payment_by_method(self, payment: Payment, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process payment based on payment method

        Args:
            payment: Payment object
            payment_data: Payment data from gateway

        Returns:
            Dict with processing result
        """
        method = payment.Methods.lower()

        if method == 'cash':
            return self._process_cash_payment(payment, payment_data)
        elif method == 'bank transfer':
            return self._process_bank_transfer(payment, payment_data)
        elif method == 'digital wallet':
            return self._process_digital_wallet(payment, payment_data)
        elif method == 'credit card':
            return self._process_credit_card(payment, payment_data)
        else:
            raise ValueError(f"Unsupported payment method: {payment.Methods}")

    def _process_cash_payment(self, payment: Payment, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process cash payment (manual confirmation)"""
        return {
            'status': 'success',
            'message': 'Cash payment confirmed',
            'transaction_reference': f"CASH_{uuid.uuid4().hex[:8].upper()}"
        }

    def _process_bank_transfer(self, payment: Payment, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process bank transfer payment"""
        # In real implementation, integrate with bank API
        return {
            'status': 'success',
            'message': 'Bank transfer completed',
            'transaction_reference': f"BANK_{uuid.uuid4().hex[:8].upper()}"
        }

    def _process_digital_wallet(self, payment: Payment, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process digital wallet payment"""
        # In real implementation, integrate with wallet API (Momo, ZaloPay, etc.)
        return {
            'status': 'success',
            'message': 'Digital wallet payment completed',
            'transaction_reference': f"WALLET_{uuid.uuid4().hex[:8].upper()}"
        }

    def _process_credit_card(self, payment: Payment, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process credit card payment"""
        # In real implementation, integrate with payment gateway (Stripe, PayPal, etc.)
        return {
            'status': 'success',
            'message': 'Credit card payment completed',
            'transaction_reference': f"CARD_{uuid.uuid4().hex[:8].upper()}"
        }

    def get_payment_history(self, user_id: int, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """
        Get paginated payment history for user

        Args:
            user_id: User ID
            limit: Number of records to return
            offset: Number of records to skip

        Returns:
            Dict with payments and pagination info
        """
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        payments = self.payment_repository.get_user_payments_paginated(user_id, limit, offset)
        total_count = self.payment_repository.get_user_payments_count(user_id)

        return {
            'payments': payments,
            'total_count': total_count,
            'limit': limit,
            'offset': offset,
            'has_more': (offset + limit) < total_count
        }

    def get_payment_statistics(self, user_id: int) -> Dict[str, Any]:
        """
        Get payment statistics for user

        Args:
            user_id: User ID

        Returns:
            Dict with payment statistics
        """
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        payments = self.payment_repository.get_by_user_id(user_id)

        total_payments = len(payments)
        successful_payments = len([p for p in payments if p.Status == 'success'])
        failed_payments = len([p for p in payments if p.Status == 'failed'])
        pending_payments = len([p for p in payments if p.Status == 'pending'])

        total_amount = sum(p.amount for p in payments if p.Status == 'success')

        # Payment method breakdown
        method_stats = {}
        for payment in payments:
            method = payment.Methods
            if method not in method_stats:
                method_stats[method] = {'count': 0, 'amount': 0}
            method_stats[method]['count'] += 1
            if payment.Status == 'success':
                method_stats[method]['amount'] += payment.amount

        return {
            'total_payments': total_payments,
            'successful_payments': successful_payments,
            'failed_payments': failed_payments,
            'pending_payments': pending_payments,
            'total_amount': total_amount,
            'success_rate': (successful_payments / total_payments * 100) if total_payments > 0 else 0,
            'method_breakdown': method_stats
        }
