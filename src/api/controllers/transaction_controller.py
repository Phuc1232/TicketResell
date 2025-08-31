from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from utils.jwt_helpers import get_current_user_id
from marshmallow import Schema, fields, validate
import uuid
from datetime import datetime
import logging

# Import services
from services.transaction_service import TransactionService
from services.payment_service import PaymentService

from services.earning_service import EarningService
from services.ticket_service import TicketService
from infrastructure.repositories.transaction_repository import TransactionRepository
from infrastructure.repositories.payment_repository import PaymentRepository

from infrastructure.repositories.earning_repository import EarningRepository
from infrastructure.repositories.ticket_repository import TicketRepository
from infrastructure.repositories.user_repository import UserRepository
from infrastructure.databases.mssql import session

logger = logging.getLogger(__name__)

bp = Blueprint('transactions', __name__, url_prefix='/api/transactions')

# Initialize services
transaction_repository = TransactionRepository(session)
payment_repository = PaymentRepository(session)

earning_repository = EarningRepository(session)
ticket_repository = TicketRepository(session)
user_repository = UserRepository(session)

transaction_service = TransactionService(transaction_repository, ticket_repository, user_repository)
payment_service = PaymentService(payment_repository, user_repository, transaction_repository)

earning_service = EarningService(earning_repository, user_repository)
ticket_service = TicketService(ticket_repository)

# Schemas
class BuyTicketSchema(Schema):
    ticket_id = fields.Int(required=True, validate=validate.Range(min=1),
                           error_messages={"required": "Ticket ID is required",
                                          "validator_failed": "Ticket ID must be a positive integer"})
    payment_method = fields.Str(required=True, validate=validate.OneOf(['Cash', 'Bank Transfer', 'Digital Wallet', 'Credit Card', 'Momo']),
                                error_messages={"required": "Payment method is required",
                                               "validator_failed": "Payment method must be one of: Cash, Bank Transfer, Digital Wallet, Credit Card, Momo"})
    payment_data = fields.Dict(required=False, load_default={})

class TransactionCallbackSchema(Schema):
    transaction_id = fields.Str(required=True)
    status = fields.Str(required=True, validate=validate.OneOf(['success', 'failed', 'pending']))
    payment_transaction_id = fields.Str()
    error_message = fields.Str()

class TransactionInitiateSchema(Schema):
    ticket_id = fields.Int(required=True, validate=validate.Range(min=1),
                          error_messages={"required": "Ticket ID is required",
                                         "validator_failed": "Ticket ID must be a positive integer"})
    payment_method = fields.Str(required=True, validate=validate.OneOf(['Cash', 'Bank Transfer', 'Digital Wallet', 'Credit Card', 'Momo']),
                               error_messages={"required": "Payment method is required",
                                              "validator_failed": "Payment method must be one of: Cash, Bank Transfer, Digital Wallet, Credit Card, Momo"})
    amount = fields.Float(required=True, validate=validate.Range(min=0.01),
                         error_messages={"required": "Amount is required",
                                        "validator_failed": "Amount must be greater than 0"})
    payment_data = fields.Dict(required=False, load_default={})

transaction_initiate_schema = TransactionInitiateSchema()
transaction_callback_schema = TransactionCallbackSchema()
buy_ticket_schema = BuyTicketSchema()

@bp.route('/initiate', methods=['POST'])
@jwt_required()
def initiate_transaction():
    """
    Initiate transaction for ticket purchase
    ---
    post:
      summary: Initiate transaction for ticket purchase
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                ticket_id:
                  type: integer
                  description: ID of the ticket to purchase
                payment_method:
                  type: string
                  enum: [Cash, Bank Transfer, Digital Wallet, Credit Card]
                  description: Payment method to use
                amount:
                  type: number
                  description: Transaction amount
              required:
                - ticket_id
                - payment_method
                - amount
      tags:
        - Transactions
      responses:
        200:
          description: Transaction initiated successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  transaction_id:
                    type: string
                  status:
                    type: string
                  redirect_url:
                    type: string
        400:
          description: Invalid input data
        404:
          description: Ticket not found
        409:
          description: Ticket already sold
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "No data provided"}), 400
            
        errors = transaction_initiate_schema.validate(data)
        if errors:
            return jsonify({"message": "Validation errors", "errors": errors}), 400
        
        current_user_id = get_current_user_id()
        ticket_id = data['ticket_id']
        payment_method = data['payment_method']
        amount = data['amount']

        # Initiate transaction using service
        transaction = transaction_service.initiate_transaction(
            ticket_id=ticket_id,
            buyer_id=current_user_id,
            amount=amount,
            payment_method=payment_method
        )

        # Create payment record
        payment = payment_service.create_payment(
            methods=payment_method,
            amount=amount,
            user_id=current_user_id,
            title=f"Ticket Purchase - Transaction {transaction.TransactionID}",
            transaction_id=transaction.TransactionID
        )



        logger.info(f"Transaction {transaction.TransactionID} initiated by user {current_user_id}")

        return jsonify({
            "transaction_id": transaction.TransactionID,
            "payment_id": payment.PaymentID,
            "status": transaction.Status,
            "redirect_url": f"/api/payments/{payment.PaymentID}/process",
            "message": "Transaction initiated successfully"
        }), 200
        
    except Exception as e:
        return jsonify({"message": "Error initiating transaction", "error": str(e)}), 500

@bp.route('/callback', methods=['POST'])
def transaction_callback():
    """
    Handle transaction gateway callback
    ---
    post:
      summary: Handle transaction gateway callback
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                transaction_id:
                  type: string
                status:
                  type: string
                  enum: [success, failed, pending]
                payment_transaction_id:
                  type: string
                error_message:
                  type: string
      tags:
        - Transactions
      responses:
        200:
          description: Callback processed successfully
        400:
          description: Invalid callback data
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "No data provided"}), 400
            
        errors = transaction_callback_schema.validate(data)
        if errors:
            return jsonify({"message": "Validation errors", "errors": errors}), 400
        
        transaction_id = data['transaction_id']
        status = data['status']
        payment_transaction_id = data.get('payment_transaction_id')
        error_message = data.get('error_message')

        # Process transaction callback using service
        transaction = transaction_service.process_transaction_callback(
            transaction_id=transaction_id,
            status=status,
            payment_transaction_id=payment_transaction_id
        )

        if status == "success":
            try:
                # QUAN TRỌNG: Luôn tạo earning khi thanh toán thành công
                earning = earning_service.process_transaction_earnings(
                    seller_id=transaction.SellerID,
                    transaction_amount=transaction.Amount,
                    transaction_id=transaction.TransactionID
                )
                logger.info(f"Transaction {transaction_id} completed successfully. Seller {transaction.SellerID} earned ${earning.TotalAmount:.2f}")
                
            except Exception as earning_error:
                logger.error(f"CRITICAL: Failed to create earning for transaction {transaction_id}: {earning_error}")
                # Vẫn tiếp tục nhưng log lỗi nghiêm trọng
                pass

        elif status == "failed":


            logger.warning(f"Transaction {transaction_id} failed: {error_message}")

        return jsonify({
            "message": "Transaction callback processed successfully",
            "transaction_id": transaction_id,
            "status": status,
            "processed_at": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing transaction callback: {e}")
        return jsonify({"message": "Error processing transaction callback", "error": str(e)}), 500


@bp.route('/preview-transaction', methods=['POST'])
@jwt_required()
def preview_transaction():
    """
    Preview transaction details without reserving the ticket
    ---
    post:
      summary: Preview transaction details without reserving the ticket
      description: Provides a preview of the transaction, including ticket details and earnings breakdown, without creating a transaction or reserving the ticket.
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                ticket_id:
                  type: integer
                  description: ID of the ticket to preview
              required:
                - ticket_id
      tags:
        - Transactions
      responses:
        200:
          description: Transaction preview successful
          content:
            application/json:
              schema:
                type: object
                properties:
                  ticket:
                    type: object
                    properties:
                      id:
                        type: integer
                      event_name:
                        type: string
                      price:
                        type: number
                      event_date:
                        type: string
                        format: date-time
                  earnings_breakdown:
                    type: object
                  available_payment_methods:
                    type: array
                    items:
                      type: string
                  message:
                    type: string
        400:
          description: Invalid input or user cannot purchase their own ticket
        404:
          description: Ticket not found
        409:
          description: Ticket is not available for purchase
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "No data provided"}), 400

        ticket_id = data.get('ticket_id')
        if not ticket_id:
            return jsonify({"message": "Ticket ID is required"}), 400

        current_user_id = get_current_user_id()

        # Get ticket information
        ticket = ticket_service.get_ticket(ticket_id)
        if not ticket:
            return jsonify({"message": "Ticket not found"}), 404

        if ticket.Status != "Available":
            return jsonify({"message": "Ticket is not available for purchase"}), 409

        # Prevent self-purchase
        if ticket.OwnerID == current_user_id:
            return jsonify({"message": "Cannot purchase your own ticket"}), 400

        # Calculate earnings breakdown
        earnings_breakdown = earning_service.calculate_seller_earnings(
            user_id=ticket.OwnerID,
            transaction_amount=ticket.Price
        )

        # Return preview information without creating transaction
        return jsonify({
            "ticket": {
                "id": ticket.TicketID,
                "event_name": ticket.EventName,
                "price": ticket.Price,
                "event_date": ticket.EventDate.isoformat() if ticket.EventDate else None
            },
            "earnings_breakdown": earnings_breakdown,
            "available_payment_methods": ["Cash", "Bank Transfer", "Digital Wallet", "Credit Card", "Momo"],
            "message": "Transaction preview successful"
        }), 200

    except Exception as e:
        logger.error(f"Error previewing transaction: {e}")
        return jsonify({"message": "Error previewing transaction", "error": str(e)}), 500


@bp.route('/buy-ticket', methods=['POST'])
@jwt_required()
def buy_ticket():
    """
    Complete ticket purchase workflow
    ---
    post:
      summary: Complete ticket purchase workflow
      description: Orchestrates the entire ticket purchase process including payment, ownership transfer, and earnings
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                ticket_id:
                  type: integer
                  description: ID of the ticket to purchase
                payment_method:
                  type: string
                  enum: [Cash, Bank Transfer, Digital Wallet, Credit Card]
                  description: Payment method to use
                payment_data:
                  type: object
                  description: Additional payment method specific data
              required:
                - ticket_id
                - payment_method
      tags:
        - Transactions
      responses:
        200:
          description: Ticket purchased successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  transaction_id:
                    type: integer
                  payment_id:
                    type: integer
                  ticket_id:
                    type: integer
                  status:
                    type: string
                  total_amount:
                    type: number
                  seller_earnings:
                    type: number
                  commission_amount:
                    type: number
                  message:
                    type: string
        400:
          description: Invalid input data or ticket not available
        404:
          description: Ticket not found
        409:
          description: Ticket already sold
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "No data provided"}), 400

        # Validate request data
        errors = buy_ticket_schema.validate(data)
        if errors:
            return jsonify({"message": "Validation errors", "errors": errors}), 400

        current_user_id = get_current_user_id()
        ticket_id = data['ticket_id']
        payment_method = data['payment_method']
        payment_data = data.get('payment_data', {})

        # Get ticket information
        ticket = ticket_service.get_ticket(ticket_id)
        if not ticket:
            return jsonify({"message": "Ticket not found"}), 404

        # Kiểm tra trạng thái vé. Chỉ cho phép mua nếu vé đang ở trạng thái 'Available' hoặc 'Reserved'
        # 'Reserved' là trạng thái tạm thời sau khi initiate_transaction
        if ticket.Status not in ["Available", "Reserved"]:
            return jsonify({"message": "Ticket is not available for purchase"}), 409

        # Prevent self-purchase
        if ticket.OwnerID == current_user_id:
            return jsonify({"message": "Cannot purchase your own ticket"}), 400

        # Calculate earnings breakdown
        earnings_breakdown = earning_service.calculate_seller_earnings(
            user_id=ticket.OwnerID,
            transaction_amount=ticket.Price
        )

        # Step 1: Initiate transaction and reserve the ticket
        transaction = transaction_service.initiate_transaction(
            ticket_id=ticket_id,
            buyer_id=current_user_id,
            amount=ticket.Price,
            payment_method=payment_method,
            reserve_ticket=True  # Explicitly reserve the ticket at this stage
        )

        # Step 2: Create payment record
        payment = payment_service.create_payment(
            methods=payment_method,
            amount=ticket.Price,
            user_id=current_user_id,
            title=f"Ticket Purchase - {ticket.EventName}",
            transaction_id=transaction.TransactionID
        )

        # Step 3: Process payment
        payment_result = payment_service.process_payment(payment.PaymentID, payment_data)

        if payment_result['status'] == 'pending' and 'payment_url' in payment_result:
            return jsonify({
                "transaction_id": transaction.TransactionID,
                "payment_id": payment.PaymentID,
                "status": "pending",
                "payment_url": payment_result['payment_url'],
                "message": "Payment initiated, redirect to payment URL"
            }), 200

        elif payment_result['status'] == 'success':
            # Step 4: Complete transaction
            completed_transaction = transaction_service.process_transaction_callback(
                transaction_id=transaction.TransactionID,
                status="success",
                payment_transaction_id=payment_result.get('transaction_reference')
            )

            # Step 5: Process seller earnings
            earning = earning_service.process_transaction_earnings(
                seller_id=ticket.OwnerID,
                transaction_amount=ticket.Price,
                transaction_id=transaction.TransactionID
            )

            logger.info(f"Ticket {ticket_id} purchased successfully by user {current_user_id}")

            return jsonify({
                "message": "Ticket purchase completed successfully",
                "transaction_id": completed_transaction.TransactionID,
                "payment_id": payment.PaymentID,
                "ticket_id": ticket_id,
                "status": completed_transaction.Status,
                "total_amount": completed_transaction.Amount,
                "seller_earnings": earning.TotalAmount,
                "commission_amount": earnings_breakdown['commission_amount']
            }), 200

        else:
            # Handle other payment statuses (e.g., failed, cancelled)
            logger.error(f"Payment for transaction {transaction.TransactionID} failed with status: {payment_result['status']}")
            transaction_service.process_transaction_callback(
                transaction_id=transaction.TransactionID,
                status="failed",
                error_message=payment_result.get('message', 'Payment failed')
            )
            return jsonify({
                "message": payment_result.get('message', 'Payment failed'),
                "payment_id": payment.PaymentID,
                "status": "failed",
                "transaction_id": transaction.TransactionID
            }), 400

    except ValueError as e:
        logger.error(f"Validation error in buy_ticket: {e}")
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        logger.error(f"Error in buy_ticket: {e}")
        return jsonify({"message": "Error processing ticket purchase", "error": str(e)}), 500

@bp.route('/status/<transaction_id>', methods=['GET'])
@jwt_required()
def get_transaction_status(transaction_id):
    """
    Get transaction status
    ---
    get:
      summary: Get transaction status by transaction ID
      security:
        - BearerAuth: []
      parameters:
        - name: transaction_id
          in: path
          required: true
          schema:
            type: string
          description: Transaction ID to check
      tags:
        - Transactions
      responses:
        200:
          description: Transaction status retrieved successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  transaction_id:
                    type: string
                  status:
                    type: string
                  amount:
                    type: number
                  created_at:
                    type: string
                    format: date-time
        404:
          description: Transaction not found
    """
    try:
        current_user_id = get_current_user_id()
        
        # TODO: Implement transaction status retrieval
        # 1. Get transaction record from database
        # 2. Verify user has access to this transaction
        # 3. Return transaction status
        
        return jsonify({
            "transaction_id": transaction_id,
            "status": "pending",
            "amount": 0.0,
            "created_at": datetime.now().isoformat(),
            "message": "Transaction status retrieved successfully"
        }), 200
        
    except Exception as e:
        return jsonify({"message": "Error retrieving transaction status", "error": str(e)}), 500
