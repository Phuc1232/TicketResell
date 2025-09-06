from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.jwt_helpers import get_current_user_id
from marshmallow import Schema, fields, validate
from datetime import datetime
from services.feedback_service import FeedbackService
from infrastructure.repositories.feedback_repository import FeedbackRepository
from infrastructure.repositories.user_repository import UserRepository
from infrastructure.repositories.ticket_repository import TicketRepository
from infrastructure.repositories.transaction_repository import TransactionRepository
from infrastructure.databases.mssql import session
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('feedback', __name__, url_prefix='/api/feedback')

# Initialize services
feedback_repository = FeedbackRepository(session)
user_repository = UserRepository(session)
ticket_repository = TicketRepository(session)
transaction_repository = TransactionRepository(session)
feedback_service = FeedbackService(feedback_repository, user_repository, ticket_repository, transaction_repository)

# Schemas
class FeedbackSchema(Schema):
    target_user_id = fields.Int(required=True, validate=validate.Range(min=1),
                               error_messages={"required": "Target user ID is required",
                                              "validator_failed": "Target user ID must be a positive integer"})
    rating = fields.Float(required=True, validate=validate.Range(min=1, max=5),
                         error_messages={"required": "Rating is required",
                                        "validator_failed": "Rating must be between 1 and 5"})
    comment = fields.Str(validate=validate.Length(max=500),
                        error_messages={"validator_failed": "Comment must be less than 500 characters"})
    transaction_id = fields.Int(validate=validate.Range(min=1))

class TicketFeedbackSchema(Schema):
    rating = fields.Float(required=True, validate=validate.Range(min=1, max=5),
                         error_messages={"required": "Rating is required",
                                        "validator_failed": "Rating must be between 1 and 5"})
    comment = fields.Str(validate=validate.Length(max=500),
                        error_messages={"validator_failed": "Comment must be less than 500 characters"})

feedback_schema = FeedbackSchema()
ticket_feedback_schema = TicketFeedbackSchema()

@bp.route('/user/<int:target_user_id>', methods=['POST'])
@jwt_required()
def submit_user_feedback(target_user_id):
    """
    Submit feedback for a user
    ---
    post:
      summary: Submit feedback for a specific user
      security:
        - BearerAuth: []
      parameters:
        - name: target_user_id
          in: path
          required: true
          schema:
            type: integer
          description: ID of the user to submit feedback for
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                rating:
                  type: number
                  minimum: 1
                  maximum: 5
                  description: Rating from 1 to 5
                comment:
                  type: string
                  maxLength: 500
                  description: Optional comment
                transaction_id:
                  type: integer
                  description: Optional transaction ID if feedback is related to a transaction
              required:
                - rating
      tags:
        - Feedback
      responses:
        201:
          description: Feedback submitted successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  feedback_id:
                    type: integer
                  rating:
                    type: number
                  comment:
                    type: string
                  submitted_at:
                    type: string
                    format: date-time
        400:
          description: Invalid input data
        404:
          description: Target user not found
        409:
          description: Feedback already submitted for this user/transaction
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "No data provided"}), 400
            
        errors = feedback_schema.validate(data)
        if errors:
            return jsonify({"message": "Validation errors", "errors": errors}), 400
        
        current_user_id = get_current_user_id()
        rating = data['rating']
        comment = data.get('comment', '')
        transaction_id = data.get('transaction_id')

        # Submit feedback using service
        feedback = feedback_service.submit_user_feedback(
            reviewer_id=current_user_id,
            target_user_id=target_user_id,
            rating=rating,
            comment=comment,
            transaction_id=transaction_id
        )

        return jsonify({
            "feedback_id": feedback.FeedbackID,
            "target_user_id": feedback.TargetUserID,
            "rating": feedback.Rating,
            "comment": feedback.Comment,
            "transaction_id": feedback.TransactionID,
            "submitted_at": feedback.CreatedAt.isoformat(),
            "message": "Feedback submitted successfully"
        }), 201
        
    except Exception as e:
        return jsonify({"message": "Error submitting feedback", "error": str(e)}), 500

@bp.route('/ticket/<int:ticket_id>', methods=['POST'])
@jwt_required()
def submit_ticket_feedback(ticket_id):
    """
    Submit feedback for a ticket
    ---
    post:
      summary: Submit feedback for a specific ticket
      security:
        - BearerAuth: []
      parameters:
        - name: ticket_id
          in: path
          required: true
          schema:
            type: integer
          description: ID of the ticket to submit feedback for
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                rating:
                  type: number
                  minimum: 1
                  maximum: 5
                  description: Rating from 1 to 5
                comment:
                  type: string
                  maxLength: 500
                  description: Optional comment
              required:
                - rating
      tags:
        - Feedback
      responses:
        201:
          description: Ticket feedback submitted successfully
        400:
          description: Invalid input data
        404:
          description: Ticket not found
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "No data provided"}), 400
            
        errors = ticket_feedback_schema.validate(data)
        if errors:
            return jsonify({"message": "Validation errors", "errors": errors}), 400
        
        current_user_id = get_current_user_id()
        rating = data['rating']
        comment = data.get('comment', '')
        
        # TODO: Implement ticket feedback submission logic
        # 1. Validate ticket exists
        # 2. Check if user has purchased this ticket
        # 3. Create ticket feedback record
        # 4. Update ticket's average rating
        
        return jsonify({
            "feedback_id": 1,
            "ticket_id": ticket_id,
            "rating": rating,
            "comment": comment,
            "submitted_at": datetime.now().isoformat(),
            "message": "Ticket feedback submitted successfully"
        }), 201
        
    except Exception as e:
        return jsonify({"message": "Error submitting ticket feedback", "error": str(e)}), 500

@bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_feedback(user_id):
    """
    Get feedback for a user
    ---
    get:
      summary: Get feedback for a specific user
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: integer
          description: ID of the user to get feedback for
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
          description: Number of feedback items to retrieve
        - name: offset
          in: query
          schema:
            type: integer
            default: 0
          description: Number of feedback items to skip
      tags:
        - Feedback
      responses:
        200:
          description: User feedback retrieved successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  feedback:
                    type: array
                    items:
                      type: object
                      properties:
                        feedback_id:
                          type: integer
                        rating:
                          type: number
                        comment:
                          type: string
                        reviewer_name:
                          type: string
                        submitted_at:
                          type: string
                          format: date-time
                  average_rating:
                    type: number
                  total_reviews:
                    type: integer
        404:
          description: User not found
    """
    try:
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # TODO: Implement feedback retrieval logic
        # 1. Validate user exists
        # 2. Get feedback for user with pagination
        # 3. Calculate average rating
        # 4. Return feedback with metadata
        
        feedback = [
            {
                "feedback_id": 1,
                "rating": 5.0,
                "comment": "Great seller, very responsive!",
                "reviewer_name": "john_doe",
                "submitted_at": datetime.now().isoformat()
            },
            {
                "feedback_id": 2,
                "rating": 4.0,
                "comment": "Good experience, would recommend",
                "reviewer_name": "jane_smith",
                "submitted_at": datetime.now().isoformat()
            }
        ]
        
        average_rating = sum(f['rating'] for f in feedback) / len(feedback) if feedback else 0
        
        return jsonify({
            "feedback": feedback,
            "average_rating": round(average_rating, 2),
            "total_reviews": len(feedback),
            "limit": limit,
            "offset": offset,
            "message": "User feedback retrieved successfully"
        }), 200
        
    except Exception as e:
        return jsonify({"message": "Error retrieving user feedback", "error": str(e)}), 500

@bp.route('/ticket/<int:ticket_id>', methods=['GET'])
def get_ticket_feedback(ticket_id):
    """
    Get feedback for a ticket
    ---
    get:
      summary: Get feedback for a specific ticket
      parameters:
        - name: ticket_id
          in: path
          required: true
          schema:
            type: integer
          description: ID of the ticket to get feedback for
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
          description: Number of feedback items to retrieve
        - name: offset
          in: query
          schema:
            type: integer
            default: 0
          description: Number of feedback items to skip
      tags:
        - Feedback
      responses:
        200:
          description: Ticket feedback retrieved successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  feedback:
                    type: array
                    items:
                      type: object
                      properties:
                        feedback_id:
                          type: integer
                        rating:
                          type: number
                        comment:
                          type: string
                        reviewer_name:
                          type: string
                        submitted_at:
                          type: string
                          format: date-time
                  average_rating:
                    type: number
                  total_reviews:
                    type: integer
        404:
          description: Ticket not found
    """
    try:
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # TODO: Implement ticket feedback retrieval logic
        # 1. Validate ticket exists
        # 2. Get feedback for ticket with pagination
        # 3. Calculate average rating
        # 4. Return feedback with metadata
        
        feedback = [
            {
                "feedback_id": 1,
                "rating": 4.5,
                "comment": "Great event, ticket was as described",
                "reviewer_name": "john_doe",
                "submitted_at": datetime.now().isoformat()
            }
        ]
        
        average_rating = sum(f['rating'] for f in feedback) / len(feedback) if feedback else 0
        
        return jsonify({
            "feedback": feedback,
            "average_rating": round(average_rating, 2),
            "total_reviews": len(feedback),
            "limit": limit,
            "offset": offset,
            "message": "Ticket feedback retrieved successfully"
        }), 200
        
    except Exception as e:
        return jsonify({"message": "Error retrieving ticket feedback", "error": str(e)}), 500


@bp.route('/user/<int:user_id>/summary', methods=['GET'])
def get_user_feedback_summary(user_id):
    """
    Get comprehensive feedback summary for a user
    ---
    get:
      summary: Get comprehensive feedback summary for a user
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: integer
          description: ID of the user to get feedback summary for
      tags:
        - Feedback
      responses:
        200:
          description: User feedback summary retrieved successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  user_id:
                    type: integer
                  average_rating:
                    type: number
                  total_feedback:
                    type: integer
                  rating_distribution:
                    type: object
                  recent_feedback:
                    type: array
                  feedback_trend:
                    type: string
        404:
          description: User not found
    """
    try:
        summary = feedback_service.get_user_feedback_summary(user_id)

        return jsonify({
            **summary,
            "message": "User feedback summary retrieved successfully"
        }), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 404
    except Exception as e:
        logger.error(f"Error retrieving user feedback summary: {e}")
        return jsonify({"message": "Error retrieving user feedback summary", "error": str(e)}), 500


@bp.route('/user/<int:user_id>/analytics', methods=['GET'])
def get_user_feedback_analytics(user_id):
    """
    Get detailed feedback analytics for a user
    ---
    get:
      summary: Get detailed feedback analytics for a user
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: integer
          description: ID of the user to get analytics for
      tags:
        - Feedback
      responses:
        200:
          description: User feedback analytics retrieved successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  user_id:
                    type: integer
                  buyer_analytics:
                    type: object
                  seller_analytics:
                    type: object
                  overall_reputation_score:
                    type: number
        404:
          description: User not found
    """
    try:
        analytics = feedback_service.get_feedback_analytics(user_id)

        return jsonify({
            **analytics,
            "message": "User feedback analytics retrieved successfully"
        }), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 404
    except Exception as e:
        logger.error(f"Error retrieving user feedback analytics: {e}")
        return jsonify({"message": "Error retrieving user feedback analytics", "error": str(e)}), 500


@bp.route('/my-feedback', methods=['GET'])
@jwt_required()
def get_my_feedback():
    """
    Get current user's feedback summary
    ---
    get:
      summary: Get current user's feedback summary
      security:
        - BearerAuth: []
      tags:
        - Feedback
      responses:
        200:
          description: Current user's feedback summary retrieved successfully
        401:
          description: Unauthorized
    """
    try:
        current_user_id = get_current_user_id()
        summary = feedback_service.get_user_feedback_summary(current_user_id)

        return jsonify({
            **summary,
            "message": "Your feedback summary retrieved successfully"
        }), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 404
    except Exception as e:
        logger.error(f"Error retrieving user's own feedback summary: {e}")
        return jsonify({"message": "Error retrieving your feedback summary", "error": str(e)}), 500


@bp.route('/my-analytics', methods=['GET'])
@jwt_required()
def get_my_feedback_analytics():
    """
    Get current user's detailed feedback analytics
    ---
    get:
      summary: Get current user's detailed feedback analytics
      security:
        - BearerAuth: []
      tags:
        - Feedback
      responses:
        200:
          description: Current user's feedback analytics retrieved successfully
        401:
          description: Unauthorized
    """
    try:
        current_user_id = get_current_user_id()
        analytics = feedback_service.get_feedback_analytics(current_user_id)

        return jsonify({
            **analytics,
            "message": "Your feedback analytics retrieved successfully"
        }), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 404
    except Exception as e:
        logger.error(f"Error retrieving user's own feedback analytics: {e}")
        return jsonify({"message": "Error retrieving your feedback analytics", "error": str(e)}), 500
