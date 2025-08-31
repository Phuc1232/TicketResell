from typing import List, Optional, Dict, Any
from domain.models.payment import Payment
from domain.models.ipayment_repository import IPaymentRepository
from domain.models.iuser_repository import IUserRepository
from domain.models.itransaction_repository import ITransactionRepository
from domain.models.itticket_repository import ITicketRepository
from datetime import datetime, timedelta
import uuid
import logging
from utils.momo_payment_gateway import MomoPaymentGateway
from config import Config

logger = logging.getLogger(__name__)

class PaymentService:
    def __init__(self, payment_repository: IPaymentRepository, user_repository: IUserRepository, transaction_repository: ITransactionRepository, ticket_repository: ITicketRepository = None):
        self.payment_repository = payment_repository
        self.user_repository = user_repository
        self.transaction_repository = transaction_repository
        self.ticket_repository = ticket_repository
    
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

            response_data = {
                'payment_id': payment_id,
                'status': result['status'],
                'message': result['message'],
                'transaction_reference': result.get('transaction_reference'),
                'payment': updated_payment
            }

            if result['status'] == 'pending' and 'payment_url' in result:
                response_data['payment_url'] = result['payment_url']

            return response_data

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
        wallet_type = payment_data.get('wallet_type', '').lower()
        
        if wallet_type == 'momo':
            bank_code = payment_data.get('bank_code')
            card_token = payment_data.get('card_token')
            return self._process_momo_payment(payment, payment_data, bank_code, card_token)
        else:
            # Fallback for other wallet types or when not specified
            logger.warning(f"Unknown wallet type: {wallet_type}, using default implementation")
            return {
                'status': 'pending',
                'message': 'Digital wallet payment initiated',
                'transaction_reference': f"WALLET_{uuid.uuid4().hex[:8].upper()}"
            }
            
    def _process_momo_payment(self, payment: Payment, payment_data: Dict[str, Any], bank_code: Optional[str] = None, card_token: Optional[str] = None) -> Dict[str, Any]:
        """Process MoMo payment"""
        try:
            # Initialize MoMo gateway
            momo_gateway = MomoPaymentGateway(
                partner_code=Config.MOMO_PARTNER_CODE,
                access_key=Config.MOMO_ACCESS_KEY,
                secret_key=Config.MOMO_SECRET_KEY,
                api_endpoint=Config.MOMO_API_ENDPOINT
            )
            
            # Generate unique order ID
            order_id = f"ORDER_{payment.PaymentID}_{uuid.uuid4().hex.upper()}"
            
            # Create payment request
            request_start_time = datetime.now()
            logger.debug(f"MoMo payment request details: order_id={order_id}, amount={payment.amount}, order_info={payment.Title}, return_url={Config.MOMO_RETURN_URL}, notify_url={Config.MOMO_NOTIFY_URL}. Request initiated at: {request_start_time}")
            momo_response = momo_gateway.create_payment_request(
                order_id=order_id,
                amount=int(payment.amount),  # MoMo requires integer amount
                order_info=f"Payment for {payment.Title}",
                return_url=Config.MOMO_RETURN_URL,
                notify_url=Config.MOMO_NOTIFY_URL,
                extra_data=str(payment.PaymentID),  # Store payment ID for reference
                bank_code=bank_code,
                card_token=card_token
            )
            logger.debug(f"Payment Title: {payment.Title}")

            request_end_time = datetime.now()
            time_taken = (request_end_time - request_start_time).total_seconds()
            logger.debug(f"MoMo payment request for order {order_id} completed in {time_taken:.2f} seconds. Response: {momo_response}")
            logger.debug(f"MoMo API Response: {momo_response}")
            if momo_response and momo_response.get('resultCode') == 0 and momo_response.get('payUrl'):
                return {
                    'status': 'pending',
                    'message': 'MoMo payment initiated successfully',
                    'transaction_reference': momo_response.get('orderId'),
                    'payment_url': momo_response.get('payUrl')
                }
            else:
                logger.error(f"MoMo payment initiation failed: {momo_response.get('message', 'Unknown error')}")
                return {
                    'status': 'failed',
                    'message': momo_response.get('message', 'MoMo payment initiation failed'),
                    'transaction_reference': momo_response.get('orderId')
                }

        except Exception as e:
            logger.error(f"Error processing MoMo payment: {e}")
            return {
                'status': 'failed',
                'message': f"Error processing MoMo payment: {e}"
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
        
        return {
            'total_payments': total_payments,
            'successful_payments': successful_payments,
            'failed_payments': failed_payments,
            'pending_payments': pending_payments,
            'total_amount': total_amount
        }
        
    def update_transaction_reference(self, transaction_id: int, reference: str) -> Any:
        """
        Update transaction reference with payment gateway reference
        
        Args:
            transaction_id: Transaction ID
            reference: Payment gateway reference (e.g., MoMo transaction ID)
            
        Returns:
            Updated transaction
        """
        transaction = self.transaction_repository.get_by_id(transaction_id)
        if not transaction:
            raise ValueError(f"Transaction not found with ID: {transaction_id}")
            
        transaction.ReferenceNumber = reference
        updated_transaction = self.transaction_repository.update(transaction)
        
        logger.info(f"Updated transaction {transaction_id} with reference {reference}")
        return updated_transaction
        
    def complete_transaction(self, transaction_id: int) -> Any:
        """
        Complete a transaction after successful payment
        
        Args:
            transaction_id: Transaction ID
            
        Returns:
            Updated transaction
        """
        transaction = self.transaction_repository.get_by_id(transaction_id)
        if not transaction:
            raise ValueError(f"Transaction not found with ID: {transaction_id}")
            
        # Update transaction status
        transaction.Status = 'completed'
        updated_transaction = self.transaction_repository.update(transaction)
        
        # If this is a ticket purchase, update ticket status
        if transaction.TicketID:
            ticket = self.ticket_repository.get_by_id(transaction.TicketID)
            if ticket:
                ticket.Status = 'sold'
                self.ticket_repository.update(ticket)
                logger.info(f"Updated ticket {ticket.TicketID} status to 'sold'")
            
        logger.info(f"Completed transaction {transaction_id}")
        return updated_transaction

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


    def handle_momo_callback(self, callback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle callback from MoMo payment gateway and update payment status

        Args:
            callback_data: Callback data from MoMo

        Returns:
            Dict with processing result
        """
        logger.info(f"Received MoMo payment callback: {callback_data}")

        try:
            # Initialize MoMo gateway
            momo_gateway = MomoPaymentGateway(
                partner_code=Config.MOMO_PARTNER_CODE,
                access_key=Config.MOMO_ACCESS_KEY,
                secret_key=Config.MOMO_SECRET_KEY,
                api_endpoint=Config.MOMO_API_ENDPOINT
            )

            # Process callback data
            process_result = momo_gateway.process_payment_callback(callback_data)
            
            if not process_result['success']:
                logger.error(f"MoMo callback processing failed: {process_result['message']}")
                
                # Nếu xử lý callback thất bại, kiểm tra xem có payment_id không
                if 'payment_id' in process_result:
                    payment_id = int(process_result['payment_id'])
                    payment = self.payment_repository.get_by_id(payment_id)
                    
                    if payment and payment.TransactionID:
                        # Cập nhật trạng thái payment thành 'failed'
                        payment.Status = 'failed'
                        self.payment_repository.update(payment)
                        
                        # Cập nhật trạng thái transaction và vé
                        transaction = self.transaction_repository.get_by_id(payment.TransactionID)
                        if transaction:
                            transaction.Status = 'failed'
                            self.transaction_repository.update(transaction)
                            
                            # Lấy thông tin vé và cập nhật trạng thái thành 'Available'
                            ticket = self.ticket_repository.get_by_id(transaction.TicketID)
                            if ticket:
                                ticket.Status = 'Available'
                                self.ticket_repository.update(ticket)
                                logger.info(f"Updated ticket {ticket.TicketID} status to 'Available' due to failed payment")
                
                return process_result

            # Extract payment ID from callback data
            payment_id = int(process_result['payment_id'])
            transaction_id = process_result['transaction_id']

            # Get payment from database
            payment = self.payment_repository.get_by_id(payment_id)
            if not payment:
                error_msg = f"Payment not found with ID: {payment_id}"
                logger.error(error_msg)
                return {
                    'success': False,
                    'message': error_msg
                }

            # Update payment status based on error_code
            if process_result.get('error_code', 0) == 0 and process_result.get('status') == 'success':
                # Thanh toán thành công
                payment.Status = 'success'
                payment.Paid_at = datetime.now()
                payment.transaction_reference = transaction_id
                
                # Update payment in database
                updated_payment = self.payment_repository.update(payment)
                
                # If payment is associated with a transaction, update transaction status
                if payment.TransactionID:
                    transaction = self.transaction_repository.get_by_id(payment.TransactionID)
                    if transaction:
                        transaction.Status = 'paid'
                        self.transaction_repository.update(transaction)
                        logger.info(f"Updated transaction {transaction.TransactionID} status to 'paid'")
                        
                        # Cập nhật trạng thái vé thành 'Sold'
                        ticket = self.ticket_repository.get_by_id(transaction.TicketID)
                        if ticket:
                            ticket.Status = 'Sold'
                            self.ticket_repository.update(ticket)
                            logger.info(f"Updated ticket {ticket.TicketID} status to 'Sold' due to successful payment")

                logger.info(f"Successfully updated payment {payment_id} status to 'success'")
                
                return {
                    'success': True,
                    'message': 'Payment status updated successfully',
                    'payment': updated_payment
                }
            else:
                # Thanh toán thất bại
                payment.Status = 'failed'
                updated_payment = self.payment_repository.update(payment)
                
                # Nếu payment liên kết với transaction, cập nhật trạng thái transaction và vé
                if payment.TransactionID:
                    transaction = self.transaction_repository.get_by_id(payment.TransactionID)
                    if transaction:
                        transaction.Status = 'failed'
                        self.transaction_repository.update(transaction)
                        
                        # Cập nhật trạng thái vé thành 'Available'
                        ticket = self.ticket_repository.get_by_id(transaction.TicketID)
                        if ticket:
                            ticket.Status = 'Available'
                            self.ticket_repository.update(ticket)
                            logger.info(f"Updated ticket {ticket.TicketID} status to 'Available' due to failed payment")
                
                logger.info(f"Payment {payment_id} failed with error code: {process_result.get('error_code')}")
                
                return {
                    'success': False,
                    'message': f"Payment failed: {process_result.get('message', 'Unknown error')}",
                    'payment': updated_payment
                }

        except Exception as e:
            error_msg = f"Error handling MoMo callback: {e}"
            logger.error(error_msg)
            return {
                'success': False,
                'message': error_msg
            }
