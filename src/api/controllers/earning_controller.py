from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.jwt_helpers import get_current_user_id
from marshmallow import Schema, fields, validate
from datetime import datetime
from services.earning_service import EarningService
from infrastructure.repositories.earning_repository import EarningRepository
from infrastructure.repositories.user_repository import UserRepository
from infrastructure.databases.mssql import session
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('earning', __name__, url_prefix='/api/earnings')

# Initialize services
earning_repository = EarningRepository(session)
user_repository = UserRepository(session)
earning_service = EarningService(earning_repository, user_repository)

# Schemas
class EarningCreateSchema(Schema):
    total_amount = fields.Float(required=True, validate=validate.Range(min=0.01))

class EarningUpdateSchema(Schema):
    total_amount = fields.Float(required=True, validate=validate.Range(min=0.01))

class DateRangeSchema(Schema):
    start_date = fields.DateTime(required=True)
    end_date = fields.DateTime(required=True)

earning_create_schema = EarningCreateSchema()
earning_update_schema = EarningUpdateSchema()
date_range_schema = DateRangeSchema()

@bp.route('/', methods=['POST'])
@jwt_required()
def create_earning():
    """
    Create a new earning record
    ---
    post:
      summary: Create a new earning record
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                total_amount:
                  type: number
                  minimum: 0.01
              required:
                - total_amount
      tags:
        - Earnings
      responses:
        201:
          description: Earning created successfully
        400:
          description: Invalid input data
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "No data provided"}), 400
            
        errors = earning_create_schema.validate(data)
        if errors:
            return jsonify({"message": "Validation errors", "errors": errors}), 400
        
        current_user_id = get_current_user_id()
        
        earning = earning_service.create_earning(
            user_id=current_user_id,
            total_amount=data['total_amount']
        )
        
        return jsonify({
            "earning_id": earning.EarningID,
            "user_id": earning.UserID,
            "total_amount": earning.TotalAmount,
            "date": earning.Date.isoformat(),
            "message": "Earning created successfully"
        }), 201
        
    except ValueError as e:
        return jsonify({"message": str(e)}), 404
    except Exception as e:
        return jsonify({"message": "Error creating earning", "error": str(e)}), 500

@bp.route('/', methods=['GET'])
@jwt_required()
def get_user_earnings():
    """
    Get current user's earnings
    ---
    get:
      summary: Get current user's earnings
      security:
        - BearerAuth: []
      tags:
        - Earnings
      responses:
        200:
          description: Earnings retrieved successfully
    """
    try:
        current_user_id = get_current_user_id()
        
        earnings = earning_service.get_user_earnings(current_user_id)
        total_earnings = earning_service.get_total_user_earnings(current_user_id)
        
        earning_list = []
        for earning in earnings:
            earning_list.append({
                "earning_id": earning.EarningID,
                "total_amount": earning.TotalAmount,
                "date": earning.Date.isoformat()
            })
        
        return jsonify({
            "earnings": earning_list,
            "total_earnings": total_earnings,
            "count": len(earning_list),
            "message": "Earnings retrieved successfully"
        }), 200
        
    except ValueError as e:
        return jsonify({"message": str(e)}), 404
    except Exception as e:
        return jsonify({"message": "Error retrieving earnings", "error": str(e)}), 500

@bp.route('/<int:earning_id>', methods=['GET'])
@jwt_required()
def get_earning(earning_id):
    """
    Get earning by ID
    ---
    get:
      summary: Get earning by ID
      security:
        - BearerAuth: []
      parameters:
        - name: earning_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Earnings
      responses:
        200:
          description: Earning retrieved successfully
        404:
          description: Earning not found
    """
    try:
        earning = earning_service.get_earning(earning_id)
        if not earning:
            return jsonify({'message': 'Earning not found'}), 404
        
        return jsonify({
            "earning_id": earning.EarningID,
            "user_id": earning.UserID,
            "total_amount": earning.TotalAmount,
            "date": earning.Date.isoformat(),
            "message": "Earning retrieved successfully"
        }), 200
        
    except Exception as e:
        return jsonify({"message": "Error retrieving earning", "error": str(e)}), 500

@bp.route('/total', methods=['GET'])
@jwt_required()
def get_total_earnings():
    """
    Get total earnings for current user
    ---
    get:
      summary: Get total earnings for current user
      security:
        - BearerAuth: []
      tags:
        - Earnings
      responses:
        200:
          description: Total earnings retrieved successfully
    """
    try:
        current_user_id = get_current_user_id()
        
        total_earnings = earning_service.get_total_user_earnings(current_user_id)
        
        return jsonify({
            "user_id": current_user_id,
            "total_earnings": total_earnings,
            "message": "Total earnings retrieved successfully"
        }), 200
        
    except ValueError as e:
        return jsonify({"message": str(e)}), 404
    except Exception as e:
        return jsonify({"message": "Error retrieving total earnings", "error": str(e)}), 500

@bp.route('/date-range', methods=['POST'])
@jwt_required()
def get_earnings_by_date_range():
    """
    Get earnings by date range
    ---
    post:
      summary: Get earnings by date range
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                start_date:
                  type: string
                  format: date-time
                end_date:
                  type: string
                  format: date-time
              required:
                - start_date
                - end_date
      tags:
        - Earnings
      responses:
        200:
          description: Earnings retrieved successfully
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "No data provided"}), 400
            
        errors = date_range_schema.validate(data)
        if errors:
            return jsonify({"message": "Validation errors", "errors": errors}), 400
        
        current_user_id = get_current_user_id()
        
        earnings = earning_service.get_earnings_by_date_range(
            user_id=current_user_id,
            start_date=data['start_date'],
            end_date=data['end_date']
        )
        
        earning_list = []
        total_amount = 0
        for earning in earnings:
            earning_list.append({
                "earning_id": earning.EarningID,
                "total_amount": earning.TotalAmount,
                "date": earning.Date.isoformat()
            })
            total_amount += earning.TotalAmount
        
        return jsonify({
            "earnings": earning_list,
            "total_amount": total_amount,
            "count": len(earning_list),
            "start_date": data['start_date'],
            "end_date": data['end_date'],
            "message": "Earnings retrieved successfully"
        }), 200
        
    except ValueError as e:
        return jsonify({"message": str(e)}), 404
    except Exception as e:
        return jsonify({"message": "Error retrieving earnings", "error": str(e)}), 500


@bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_earnings_statistics():
    """
    Get comprehensive earnings statistics for current user
    ---
    get:
      summary: Get comprehensive earnings statistics
      security:
        - BearerAuth: []
      tags:
        - Earnings
      responses:
        200:
          description: Earnings statistics retrieved successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  user_id:
                    type: integer
                  total_earnings:
                    type: number
                  total_transactions:
                    type: integer
                  average_earning:
                    type: number
                  monthly_earnings:
                    type: object
                  recent_earnings:
                    type: array
                  earnings_trend:
                    type: string
        404:
          description: User not found
    """
    try:
        current_user_id = get_current_user_id()

        stats = earning_service.get_earnings_statistics(current_user_id)

        return jsonify({
            **stats,
            "message": "Earnings statistics retrieved successfully"
        }), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 404
    except Exception as e:
        logger.error(f"Error retrieving earnings statistics: {e}")
        return jsonify({"message": "Error retrieving earnings statistics", "error": str(e)}), 500


@bp.route('/summary', methods=['GET'])
@jwt_required()
def get_earnings_summary():
    """
    Get earnings summary for different time periods
    ---
    get:
      summary: Get earnings summary for different time periods
      security:
        - BearerAuth: []
      parameters:
        - name: period
          in: query
          schema:
            type: string
            enum: [all, year, month, week]
            default: all
          description: Time period for summary
      tags:
        - Earnings
      responses:
        200:
          description: Earnings summary retrieved successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  user_id:
                    type: integer
                  period:
                    type: string
                  total_amount:
                    type: number
                  transaction_count:
                    type: integer
                  average_amount:
                    type: number
                  highest_earning:
                    type: number
                  lowest_earning:
                    type: number
        400:
          description: Invalid period
        404:
          description: User not found
    """
    try:
        current_user_id = get_current_user_id()

        period = request.args.get('period', 'all')
        valid_periods = ['all', 'year', 'month', 'week']

        if period not in valid_periods:
            return jsonify({
                "message": f"Invalid period. Must be one of: {valid_periods}"
            }), 400

        summary = earning_service.get_earnings_summary(current_user_id, period)

        return jsonify({
            **summary,
            "message": f"Earnings summary for '{period}' period retrieved successfully"
        }), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 404
    except Exception as e:
        logger.error(f"Error retrieving earnings summary: {e}")
        return jsonify({"message": "Error retrieving earnings summary", "error": str(e)}), 500


@bp.route('/calculate', methods=['POST'])
@jwt_required()
def calculate_earnings():
    """
    Calculate earnings from transaction amount
    ---
    post:
      summary: Calculate earnings from transaction amount
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                transaction_amount:
                  type: number
                  minimum: 0
                platform_commission:
                  type: number
                  minimum: 0
                  maximum: 1
                  default: 0.05
              required:
                - transaction_amount
      tags:
        - Earnings
      responses:
        200:
          description: Earnings calculated successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  transaction_amount:
                    type: number
                  platform_commission_rate:
                    type: number
                  commission_amount:
                    type: number
                  seller_earnings:
                    type: number
                  net_percentage:
                    type: number
        400:
          description: Invalid input data
    """
    try:
        current_user_id = get_current_user_id()

        data = request.get_json()
        if not data:
            return jsonify({"message": "Request body is required"}), 400

        transaction_amount = data.get('transaction_amount')
        if transaction_amount is None or transaction_amount < 0:
            return jsonify({"message": "Valid transaction_amount is required"}), 400

        platform_commission = data.get('platform_commission', 0.05)
        if platform_commission < 0 or platform_commission > 1:
            return jsonify({"message": "Platform commission must be between 0 and 1"}), 400

        calculation = earning_service.calculate_seller_earnings(
            current_user_id, transaction_amount, platform_commission
        )

        return jsonify({
            **calculation,
            "message": "Earnings calculated successfully"
        }), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 404
    except Exception as e:
        logger.error(f"Error calculating earnings: {e}")
        return jsonify({"message": "Error calculating earnings", "error": str(e)}), 500
