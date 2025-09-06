from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.jwt_helpers import get_current_user_id
from marshmallow import Schema, fields, validate
from datetime import datetime
from services.payment_service import PaymentService
from infrastructure.repositories.payment_repository import PaymentRepository
from infrastructure.repositories.user_repository import UserRepository
from infrastructure.repositories.transaction_repository import TransactionRepository
from infrastructure.databases.mssql import session

bp = Blueprint('payment', __name__, url_prefix='/api/payments')

# Initialize services
payment_repository = PaymentRepository(session)
user_repository = UserRepository(session)
transaction_repository = TransactionRepository(session)
payment_service = PaymentService(payment_repository, user_repository, transaction_repository)

# Schemas
class PaymentCreateSchema(Schema):
    methods = fields.Str(required=True, validate=validate.OneOf(['Cash', 'Bank Transfer', 'Digital Wallet', 'Credit Card']))
    amount = fields.Float(required=True, validate=validate.Range(min=0.01))
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    transaction_id = fields.Int()

class PaymentUpdateSchema(Schema):
    status = fields.Str(required=True, validate=validate.OneOf(['pending', 'success', 'failed', 'cancelled']))

class PaymentProcessSchema(Schema):
    payment_method_data = fields.Dict(load_default={})
    confirmation_code = fields.Str()
    gateway_response = fields.Dict(load_default={})

payment_create_schema = PaymentCreateSchema()
payment_update_schema = PaymentUpdateSchema()
payment_process_schema = PaymentProcessSchema()

@bp.route('/', methods=['POST'])
@jwt_required()
def create_payment():
    """
    Create a new payment
    ---
    post:
      summary: Create a new payment
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                methods:
                  type: string
                  enum: [Cash, Bank Transfer, Digital Wallet, Credit Card]
                amount:
                  type: number
                  minimum: 0.01
                title:
                  type: string
                  maxLength: 200
                transaction_id:
                  type: integer
              required:
                - methods
                - amount
                - title
      tags:
        - Payments
      responses:
        201:
          description: Payment created successfully
        400:
          description: Invalid input data
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "No data provided"}), 400
            
        errors = payment_create_schema.validate(data)
        if errors:
            return jsonify({"message": "Validation errors", "errors": errors}), 400
        
        current_user_id = get_current_user_id()
        
        payment = payment_service.create_payment(
            methods=data['methods'],
            amount=data['amount'],
            user_id=current_user_id,
            title=data['title'],
            transaction_id=data.get('transaction_id')
        )
        
        return jsonify({
            "payment_id": payment.PaymentID,
            "methods": payment.Methods,
            "status": payment.Status,
            "amount": payment.amount,
            "title": payment.Title,
            "user_id": payment.UserID,
            "transaction_id": payment.TransactionID,
            "message": "Payment created successfully"
        }), 201
        
    except ValueError as e:
        return jsonify({"message": str(e)}), 404
    except Exception as e:
        return jsonify({"message": "Error creating payment", "error": str(e)}), 500

@bp.route('/', methods=['GET'])
@jwt_required()
def get_user_payments():
    """
    Get current user's payments
    ---
    get:
      summary: Get current user's payments
      security:
        - BearerAuth: []
      tags:
        - Payments
      responses:
        200:
          description: Payments retrieved successfully
    """
    try:
        current_user_id = get_current_user_id()
        
        payments = payment_service.get_user_payments(current_user_id)
        
        payment_list = []
        for payment in payments:
            payment_list.append({
                "payment_id": payment.PaymentID,
                "methods": payment.Methods,
                "status": payment.Status,
                "amount": payment.amount,
                "title": payment.Title,
                "paid_at": payment.Paid_at.isoformat() if payment.Paid_at else None,
                "transaction_id": payment.TransactionID
            })
        
        return jsonify({
            "payments": payment_list,
            "total": len(payment_list),
            "message": "Payments retrieved successfully"
        }), 200
        
    except ValueError as e:
        return jsonify({"message": str(e)}), 404
    except Exception as e:
        return jsonify({"message": "Error retrieving payments", "error": str(e)}), 500

@bp.route('/<int:payment_id>', methods=['GET'])
@jwt_required()
def get_payment(payment_id):
    """
    Get payment by ID
    ---
    get:
      summary: Get payment by ID
      security:
        - BearerAuth: []
      parameters:
        - name: payment_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Payments
      responses:
        200:
          description: Payment retrieved successfully
        404:
          description: Payment not found
    """
    try:
        payment = payment_service.get_payment(payment_id)
        if not payment:
            return jsonify({'message': 'Payment not found'}), 404
        
        return jsonify({
            "payment_id": payment.PaymentID,
            "methods": payment.Methods,
            "status": payment.Status,
            "amount": payment.amount,
            "title": payment.Title,
            "paid_at": payment.Paid_at.isoformat() if payment.Paid_at else None,
            "user_id": payment.UserID,
            "transaction_id": payment.TransactionID,
            "message": "Payment retrieved successfully"
        }), 200
        
    except Exception as e:
        return jsonify({"message": "Error retrieving payment", "error": str(e)}), 500

@bp.route('/<int:payment_id>/status', methods=['PUT'])
@jwt_required()
def update_payment_status(payment_id):
    """
    Update payment status
    ---
    put:
      summary: Update payment status
      security:
        - BearerAuth: []
      parameters:
        - name: payment_id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
                  enum: [pending, success, failed, cancelled]
              required:
                - status
      tags:
        - Payments
      responses:
        200:
          description: Payment status updated successfully
        404:
          description: Payment not found
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "No data provided"}), 400
            
        errors = payment_update_schema.validate(data)
        if errors:
            return jsonify({"message": "Validation errors", "errors": errors}), 400
        
        payment = payment_service.update_payment_status(payment_id, data['status'])
        if not payment:
            return jsonify({'message': 'Payment not found'}), 404
        
        return jsonify({
            "payment_id": payment.PaymentID,
            "status": payment.Status,
            "paid_at": payment.Paid_at.isoformat() if payment.Paid_at else None,
            "message": "Payment status updated successfully"
        }), 200
        
    except Exception as e:
        return jsonify({"message": "Error updating payment status", "error": str(e)}), 500


@bp.route('/<int:payment_id>/process', methods=['POST'])
@jwt_required()
def process_payment(payment_id):
    """
    Process payment through payment gateway
    ---
    post:
      summary: Process payment through payment gateway
      security:
        - BearerAuth: []
      parameters:
        - name: payment_id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: false
        content:
          application/json:
            schema:
              type: object
              properties:
                payment_method_data:
                  type: object
                  description: Additional payment method specific data
                confirmation_code:
                  type: string
                  description: Confirmation code for manual payments
                gateway_response:
                  type: object
                  description: Response from payment gateway
      tags:
        - Payments
      responses:
        200:
          description: Payment processed successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  payment_id:
                    type: integer
                  status:
                    type: string
                  message:
                    type: string
                  transaction_reference:
                    type: string
        400:
          description: Invalid payment data
        404:
          description: Payment not found
    """
    try:
        data = request.get_json() or {}

        errors = payment_process_schema.validate(data)
        if errors:
            return jsonify({"message": "Validation errors", "errors": errors}), 400

        result = payment_service.process_payment(payment_id, data)

        return jsonify({
            "payment_id": result['payment_id'],
            "status": result['status'],
            "message": result['message'],
            "transaction_reference": result.get('transaction_reference'),
            "processed_at": datetime.now().isoformat()
        }), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": "Error processing payment", "error": str(e)}), 500


@bp.route('/history', methods=['GET'])
@jwt_required()
def get_payment_history():
    """
    Get paginated payment history for current user
    ---
    get:
      summary: Get paginated payment history
      security:
        - BearerAuth: []
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
            minimum: 1
            maximum: 100
        - name: offset
          in: query
          schema:
            type: integer
            default: 0
            minimum: 0
      tags:
        - Payments
      responses:
        200:
          description: Payment history retrieved successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  payments:
                    type: array
                    items:
                      type: object
                  total_count:
                    type: integer
                  limit:
                    type: integer
                  offset:
                    type: integer
                  has_more:
                    type: boolean
    """
    try:
        current_user_id = get_current_user_id()

        limit = min(int(request.args.get('limit', 20)), 100)
        offset = max(int(request.args.get('offset', 0)), 0)

        result = payment_service.get_payment_history(current_user_id, limit, offset)

        payment_list = []
        for payment in result['payments']:
            payment_list.append({
                "payment_id": payment.PaymentID,
                "methods": payment.Methods,
                "status": payment.Status,
                "amount": payment.amount,
                "title": payment.Title,
                "paid_at": payment.Paid_at.isoformat() if payment.Paid_at else None,
                "transaction_id": payment.TransactionID
            })

        return jsonify({
            "payments": payment_list,
            "total_count": result['total_count'],
            "limit": result['limit'],
            "offset": result['offset'],
            "has_more": result['has_more'],
            "message": "Payment history retrieved successfully"
        }), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 404
    except Exception as e:
        return jsonify({"message": "Error retrieving payment history", "error": str(e)}), 500


@bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_payment_statistics():
    """
    Get payment statistics for current user
    ---
    get:
      summary: Get payment statistics
      security:
        - BearerAuth: []
      tags:
        - Payments
      responses:
        200:
          description: Payment statistics retrieved successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  total_payments:
                    type: integer
                  successful_payments:
                    type: integer
                  failed_payments:
                    type: integer
                  pending_payments:
                    type: integer
                  total_amount:
                    type: number
                  success_rate:
                    type: number
                  method_breakdown:
                    type: object
    """
    try:
        current_user_id = get_current_user_id()

        stats = payment_service.get_payment_statistics(current_user_id)

        return jsonify({
            **stats,
            "message": "Payment statistics retrieved successfully"
        }), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 404
    except Exception as e:
        return jsonify({"message": "Error retrieving payment statistics", "error": str(e)}), 500
