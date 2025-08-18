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

payment_create_schema = PaymentCreateSchema()
payment_update_schema = PaymentUpdateSchema()

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
