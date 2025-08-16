from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, validate
import uuid
from datetime import datetime

bp = Blueprint('transactions', __name__, url_prefix='/api/transactions')

# Schemas
class TransactionInitiateSchema(Schema):
    ticket_id = fields.Int(required=True, validate=validate.Range(min=1),
                          error_messages={"required": "Ticket ID is required",
                                         "validator_failed": "Ticket ID must be a positive integer"})
    payment_method = fields.Str(required=True, validate=validate.OneOf(['Cash', 'Bank Transfer', 'Digital Wallet', 'Credit Card']),
                               error_messages={"required": "Payment method is required",
                                              "validator_failed": "Payment method must be one of: Cash, Bank Transfer, Digital Wallet, Credit Card"})
    amount = fields.Float(required=True, validate=validate.Range(min=0.01),
                         error_messages={"required": "Amount is required",
                                        "validator_failed": "Amount must be greater than 0"})

class TransactionCallbackSchema(Schema):
    transaction_id = fields.Str(required=True)
    status = fields.Str(required=True, validate=validate.OneOf(['success', 'failed', 'pending']))
    payment_transaction_id = fields.Str()
    error_message = fields.Str()

transaction_initiate_schema = TransactionInitiateSchema()
transaction_callback_schema = TransactionCallbackSchema()

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
        
        current_user_id = int(get_jwt_identity())
        ticket_id = data['ticket_id']
        payment_method = data['payment_method']
        amount = data['amount']
        
        # TODO: Implement transaction service logic
        # 1. Validate ticket exists and is available
        # 2. Check if user has sufficient balance
        # 3. Create transaction record
        # 4. Redirect to payment gateway
        
        transaction_id = str(uuid.uuid4())
        
        return jsonify({
            "transaction_id": transaction_id,
            "status": "pending",
            "redirect_url": f"/transaction/gateway/{transaction_id}",
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
        
        # TODO: Implement transaction callback logic
        # 1. Update transaction record
        # 2. If successful, transfer ticket ownership
        # 3. Send notifications
        # 4. Update transaction status
        
        return jsonify({
            "message": "Transaction callback processed successfully",
            "transaction_id": transaction_id,
            "status": status
        }), 200
        
    except Exception as e:
        return jsonify({"message": "Error processing transaction callback", "error": str(e)}), 500

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
        current_user_id = int(get_jwt_identity())
        
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
