from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.jwt_helpers import get_current_user_id
from marshmallow import Schema, fields, validate
from datetime import datetime
from services.payment_service import PaymentService
from services.earning_service import EarningService
from infrastructure.repositories.payment_repository import PaymentRepository
from infrastructure.repositories.user_repository import UserRepository
from infrastructure.repositories.transaction_repository import TransactionRepository
from infrastructure.repositories.ticket_repository import TicketRepository
from infrastructure.repositories.earning_repository import EarningRepository
from infrastructure.databases.mssql import session
from utils.momo_payment_gateway import MomoPaymentGateway
from config import Config
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('payment', __name__, url_prefix='/api/payments')

# Initialize services
payment_repository = PaymentRepository(session)
user_repository = UserRepository(session)
transaction_repository = TransactionRepository(session)
ticket_repository = TicketRepository(session)
earning_repository = EarningRepository(session)

payment_service = PaymentService(payment_repository, user_repository, transaction_repository, ticket_repository)
earning_service = EarningService(earning_repository, user_repository)

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
    wallet_type = fields.Str()

class MomoCallbackSchema(Schema):
    partnerCode = fields.Str()
    orderId = fields.Str()
    requestId = fields.Str()
    amount = fields.Int()
    orderInfo = fields.Str()
    orderType = fields.Str()
    transId = fields.Str()
    resultCode = fields.Int()
    message = fields.Str()
    payType = fields.Str()
    responseTime = fields.Int()
    extraData = fields.Str()
    signature = fields.Str()

payment_create_schema = PaymentCreateSchema()
payment_update_schema = PaymentUpdateSchema()
payment_process_schema = PaymentProcessSchema()
momo_callback_schema = MomoCallbackSchema()

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
                wallet_type:
                  type: string
                  description: Type of digital wallet (momo, zalopay, etc.)
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
                  payment_url:
                    type: string
                    description: URL to redirect user for payment (for digital wallets)
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

        response = {
            "payment_id": result['payment_id'],
            "status": result['status'],
            "message": result['message'],
            "transaction_reference": result.get('transaction_reference'),
            "processed_at": datetime.now().isoformat()
        }
        
        # Add payment URL if available (for digital wallets)
        if 'payment_url' in result:
            response['payment_url'] = result['payment_url']

        return jsonify(response), 200

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


@bp.route('/momo/return', methods=['GET'])
def momo_return():
    """
    Handle MoMo return URL (redirect after payment)
    ---
    get:
      summary: Handle MoMo return URL
      parameters:
        - name: partnerCode
          in: query
          required: true
          schema:
            type: string
        - name: orderId
          in: query
          required: true
          schema:
            type: string
        - name: requestId
          in: query
          required: true
          schema:
            type: string
        - name: amount
          in: query
          required: true
          schema:
            type: integer
        - name: orderInfo
          in: query
          required: true
          schema:
            type: string
        - name: orderType
          in: query
          required: true
          schema:
            type: string
        - name: transId
          in: query
          required: true
          schema:
            type: integer
        - name: resultCode
          in: query
          required: true
          schema:
            type: integer
        - name: message
          in: query
          required: true
          schema:
            type: string
        - name: payType
          in: query
          required: true
          schema:
            type: string
        - name: responseTime
          in: query
          required: true
          schema:
            type: integer
        - name: extraData
          in: query
          required: true
          schema:
            type: string
        - name: signature
          in: query
          required: true
          schema:
            type: string
      responses:
        200:
          description: Payment return handled successfully
        400:
          description: Invalid payment data
    """
    try:
        # Get query parameters
        params = request.args.to_dict()
        
        # Validate parameters
        errors = momo_callback_schema.validate(params)
        if errors:
            logger.error(f"MoMo return validation errors: {errors}")
            return jsonify({"message": "Invalid MoMo return data", "errors": errors}), 400
        
        # For returnUrl, we don't strictly need to verify signature here as IPN will handle it
        # However, for security, it's good practice to at least check resultCode
        result_code = int(params.get('resultCode'))
        payment_id = params.get('extraData')
        transaction_id = params.get('transId')

        if result_code == 0:
            status = 'success'
            message = "Payment completed successfully"
        else:
            status = 'failed'
            message = f"Payment failed: {params.get('message')}"
        
        # You might want to redirect to a frontend page here, passing status and payment_id
        # For now, we'll just return a JSON response
        return jsonify({
            "error_code": result_code,
            "message": message,
            "payment_id": payment_id,
            "status": status,
            "transaction_id": transaction_id
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing MoMo return: {e}")
        return jsonify({"message": "Error processing payment return", "error": str(e)}), 500

@bp.route('/momo/ipn', methods=['POST'])
def momo_ipn():
    """
    Handle MoMo IPN (Instant Payment Notification)
    ---
    post:
      summary: Handle MoMo IPN
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/MomoCallbackSchema'
      responses:
        200:
          description: IPN processed successfully
        400:
          description: Invalid IPN data
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "No data provided"}), 400

        errors = momo_callback_schema.validate(data)
        if errors:
            logger.error(f"MoMo IPN validation errors: {errors}")
            return jsonify({"message": "Invalid MoMo IPN data", "errors": errors}), 400

        # Verify signature
        momo_gateway = MomoPaymentGateway(
            partner_code=Config.MOMO_PARTNER_CODE,
            access_key=Config.MOMO_ACCESS_KEY,
            secret_key=Config.MOMO_SECRET_KEY,
            api_endpoint=Config.MOMO_API_ENDPOINT
        )

        is_valid = momo_gateway.verify_ipn_signature(data)
        if not is_valid:
            logger.error("MoMo IPN signature verification failed")
            return jsonify({"message": "Invalid signature"}), 400

        payment_id = data.get('extraData')
        if not payment_id:
            logger.error("Payment ID not found in MoMo IPN data")
            return jsonify({"message": "Payment ID not found"}), 400

        result_code = int(data.get('resultCode'))
        if result_code == 0:
            status = 'success'
        else:
            status = 'failed'

        # Update payment status and transaction status
        payment = payment_service.update_payment_status(payment_id, status)
        
        # QUAN TRỌNG: Tạo earning khi payment thành công
        if status == 'success' and payment and payment.TransactionID:
            try:
                transaction = transaction_repository.get_by_id(payment.TransactionID)
                if transaction:
                    earning = earning_service.process_transaction_earnings(
                        seller_id=transaction.SellerID,
                        transaction_amount=transaction.Amount,
                        transaction_id=transaction.TransactionID
                    )
                    logger.info(f"MoMo IPN: Created earning {earning.EarningID} for seller {transaction.SellerID}")
            except Exception as earning_error:
                logger.error(f"CRITICAL: Failed to create earning in MoMo IPN for payment {payment_id}: {earning_error}")

        return jsonify({"message": "IPN processed successfully"}), 200

    except Exception as e:
        logger.error(f"Error processing MoMo IPN: {e}")
        return jsonify({"message": "Error processing IPN", "error": str(e)}), 500

@bp.route('/momo/callback/json', methods=['POST'])
def momo_callback_json():
    """
    Handle MoMo payment callback
    This endpoint is called when MoMo sends payment notification
    ---
    post:
      summary: Handle MoMo payment callback
      tags:
        - Payments
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                partnerCode:
                  type: string
                orderId:
                  type: string
                requestId:
                  type: string
                amount:
                  type: integer
                orderInfo:
                  type: string
                orderType:
                  type: string
                transId:
                  type: string
                resultCode:
                  type: integer
                message:
                  type: string
                payType:
                  type: string
                responseTime:
                  type: integer
                extraData:
                  type: string
                signature:
                  type: string
      responses:
        200:
          description: Payment callback handled successfully
        400:
          description: Invalid payment data
    """
    try:
        # Get query parameters
        params = request.args.to_dict()
        
        # Validate parameters
        errors = momo_callback_schema.validate(params)
        if errors:
            logger.error(f"MoMo return validation errors: {errors}")
            return jsonify({"message": "Invalid MoMo return data", "errors": errors}), 400
        
        # Verify signature
        momo_gateway = MomoPaymentGateway(
            partner_code=Config.MOMO_PARTNER_CODE,
            access_key=Config.MOMO_ACCESS_KEY,
            secret_key=Config.MOMO_SECRET_KEY,
            api_endpoint=Config.MOMO_API_ENDPOINT
        )
        
        is_valid = momo_gateway.verify_ipn_signature(params)
        if not is_valid:
            logger.error("MoMo return signature verification failed")
            return jsonify({"message": "Invalid signature"}), 400
        
        # Extract payment ID from extraData
        payment_id = params.get('extraData')
        if not payment_id:
            logger.error("Payment ID not found in MoMo return data")
            return jsonify({"message": "Payment ID not found"}), 400
        
        # Check result code
        result_code = int(params.get('resultCode'))
        if result_code == 0:
            # Payment successful
            status = 'success'
        else:
            # Payment failed
            status = 'failed'
        
        # Update payment status
        payment = payment_service.update_payment_status(payment_id, status)
        
        # Redirect to a success or failure page
        if status == 'success':
            return jsonify({
                "payment_id": payment_id,
                "status": status,
                "message": "Payment completed successfully",
                "transaction_id": params.get('transId')
            }), 200
        else:
            return jsonify({
                "payment_id": payment_id,
                "status": status,
                "message": f"Payment failed: {params.get('message')}",
                "error_code": result_code
            }), 200
        
    except Exception as e:
        logger.error(f"Error processing MoMo return: {e}")
        return jsonify({"message": "Error processing payment return", "error": str(e)}), 500


@bp.route('/momo/notify', methods=['POST'])
def momo_notify_url():
    """
    Handle MoMo payment notification (IPN)
    This endpoint is called by MoMo server to notify payment status
    ---
    post:
      summary: Handle MoMo payment notification
      tags:
        - Payments
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                partnerCode:
                  type: string
                orderId:
                  type: string
                requestId:
                  type: string
                amount:
                  type: integer
                orderInfo:
                  type: string
                orderType:
                  type: string
                transId:
                  type: string
                resultCode:
                  type: integer
                message:
                  type: string
                payType:
                  type: string
                responseTime:
                  type: integer
                extraData:
                  type: string
                signature:
                  type: string
      responses:
        200:
          description: Payment notification handled successfully
        400:
          description: Invalid payment data
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            logger.error("No data provided in MoMo IPN")
            return jsonify({"message": "No data provided"}), 400
        
        # Validate data
        errors = momo_callback_schema.validate(data)
        if errors:
            logger.error(f"MoMo IPN validation errors: {errors}")
            return jsonify({"message": "Invalid MoMo IPN data", "errors": errors}), 400
        
        # Verify signature
        momo_gateway = MomoPaymentGateway(
            partner_code=Config.MOMO_PARTNER_CODE,
            access_key=Config.MOMO_ACCESS_KEY,
            secret_key=Config.MOMO_SECRET_KEY,
            api_endpoint=Config.MOMO_API_ENDPOINT
        )
        
        is_valid = momo_gateway.verify_ipn_signature(data)
        if not is_valid:
            logger.error("MoMo IPN signature verification failed")
            return jsonify({"message": "Invalid signature"}), 400
        
        # Extract payment ID from extraData
        payment_id = data.get('extraData')
        if not payment_id:
            logger.error("Payment ID not found in MoMo IPN data")
            return jsonify({"message": "Payment ID not found"}), 400
        
        # Check result code
        result_code = int(data.get('resultCode'))
        if result_code == 0:
            # Payment successful
            status = 'success'
        else:
            # Payment failed
            status = 'failed'
        
        # Update payment status
        payment = payment_service.update_payment_status(payment_id, status)
        
        # Return success response to MoMo
        return jsonify({
            "error_code": 0,
            "message": "Payment completed successfully",
            "payment_id": payment_id,
            "status": status,
            "transaction_id": data.get('transId')
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing MoMo IPN: {e}")
        return jsonify({
            "message": "Error",
            "resultCode": 99
        }), 500

@bp.route('/momo/callback/process', methods=['POST'])
def momo_callback_process():
    """
    Handle MoMo payment callback
    This endpoint is called by MoMo to notify payment status
    ---
    post:
      summary: Handle MoMo payment callback
      tags:
        - Payments
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                error_code:
                  type: integer
                message:
                  type: string
                payment_id:
                  type: string
                status:
                  type: string
                transaction_id:
                  type: string
      responses:
        200:
          description: Payment callback handled successfully
        400:
          description: Invalid callback data
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            logger.error("No data provided in MoMo callback")
            return jsonify({"message": "No data provided"}), 400
        
        logger.info(f"Received MoMo callback: {data}")
        
        # Validate required fields
        required_fields = ['error_code', 'message', 'payment_id', 'status', 'transaction_id']
        for field in required_fields:
            if field not in data:
                logger.error(f"Missing required field in MoMo callback: {field}")
                return jsonify({"message": f"Missing required field: {field}"}), 400
        
        # Extract data
        error_code = data.get('error_code')
        message = data.get('message')
        payment_id = data.get('payment_id')
        status = data.get('status')
        transaction_id = data.get('transaction_id')
        
        logger.info(f"Processing payment {payment_id} with status {status}")
        
        # Determine payment status based on MoMo response
        payment_status = 'success' if error_code == 0 and status == 'success' else 'failed'
        
        try:
            # Update payment status in database
            payment = payment_service.update_payment_status(payment_id, payment_status)
            
            # If payment successful, update related transaction
            if payment_status == 'success':
                # Update transaction with MoMo transaction ID
                transaction = payment_service.update_transaction_reference(payment.TransactionID, transaction_id)
                
                # Complete the transaction (e.g., mark ticket as sold)
                payment_service.complete_transaction(payment.TransactionID)
                
                logger.info(f"Payment {payment_id} processed successfully with transaction {transaction_id}")
            else:
                logger.warning(f"Payment {payment_id} failed with error code {error_code}: {message}")
            
            return jsonify({
                "message": "Payment callback processed successfully",
                "success": True,
                "payment_id": payment_id,
                "status": payment_status
            }), 200
            
        except ValueError as e:
            logger.error(f"Value error processing MoMo callback: {e}")
            return jsonify({
                "message": str(e),
                "success": False
            }), 400
            
    except Exception as e:
        logger.error(f"Error processing MoMo callback: {e}")
        return jsonify({
            "message": "Error processing payment callback",
            "error": str(e)
        }), 500
