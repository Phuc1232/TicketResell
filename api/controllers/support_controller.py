from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.jwt_helpers import get_current_user_id
from marshmallow import Schema, fields, validate
from datetime import datetime
from services.support_service import SupportService
from infrastructure.repositories.support_repository import SupportRepository
from infrastructure.repositories.user_repository import UserRepository
from services.email_service import EmailService
from infrastructure.databases.mssql import session
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('support', __name__, url_prefix='/api/support')

# Initialize services
support_repository = SupportRepository(session)
user_repository = UserRepository(session)
email_service = EmailService()
support_service = SupportService(support_repository, user_repository, email_service)

# Schemas
class SupportCreateSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    issue_description = fields.Str(validate=validate.Length(max=2000))
    recipient_type = fields.Str(required=False, validate=validate.OneOf(['admin', 'user']))
    recipient_id = fields.Int(required=False)

class SupportUpdateSchema(Schema):
    title = fields.Str(validate=validate.Length(min=1, max=200))
    issue_description = fields.Str(validate=validate.Length(max=2000))
    status = fields.Str(validate=validate.OneOf(['open', 'in_progress', 'resolved', 'closed']))

class SupportStatusSchema(Schema):
    status = fields.Str(required=True, validate=validate.OneOf(['open', 'in_progress', 'resolved', 'closed']))

support_create_schema = SupportCreateSchema()
support_update_schema = SupportUpdateSchema()
support_status_schema = SupportStatusSchema()

@bp.route('/', methods=['POST'])
@jwt_required()
def create_support_ticket():
    """
    Create a new support ticket
    ---
    post:
      summary: Create a new support ticket
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                title:
                  type: string
                  maxLength: 200
                issue_description:
                  type: string
                  maxLength: 2000
                recipient_type:
                  type: string
                  enum: ['admin', 'user']
                  default: 'admin'
                  description: Optional - defaults to 'admin'
                recipient_id:
                  type: integer
                  description: Optional - ID of the recipient if recipient_type is 'user'
              required:
                - title
      tags:
        - Support
      responses:
        201:
          description: Support ticket created successfully
        400:
          description: Invalid input data
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "No data provided"}), 400
            
        errors = support_create_schema.validate(data)
        if errors:
            return jsonify({"message": "Validation errors", "errors": errors}), 400
        
        current_user_id = get_current_user_id()
        
        # Sử dụng recipient_type từ request hoặc mặc định là 'admin'
        recipient_type = data.get('recipient_type', 'admin')
        recipient_id = data.get('recipient_id') if recipient_type == 'user' else None
        
        support = support_service.create_support_ticket(
            user_id=current_user_id,
            title=data['title'],
            issue_description=data.get('issue_description'),
            recipient_type=recipient_type,
            recipient_id=recipient_id
        )
        
        return jsonify({
            "support_id": support.SupportID,
            "user_id": support.UserID,
            "title": support.Title,
            "status": support.Status,
            "issue_description": support.Issue_des,
            "created_at": support.Create_at.isoformat(),
            "message": "Support ticket created successfully"
        }), 201
        
    except ValueError as e:
        return jsonify({"message": str(e)}), 404
    except Exception as e:
        return jsonify({"message": "Error creating support ticket", "error": str(e)}), 500

@bp.route('/', methods=['GET'])
@jwt_required()
def get_user_support_tickets():
    """
    Get current user's support tickets
    ---
    get:
      summary: Get current user's support tickets
      security:
        - BearerAuth: []
      tags:
        - Support
      responses:
        200:
          description: Support tickets retrieved successfully
    """
    try:
        current_user_id = get_current_user_id()
        
        support_tickets = support_service.get_user_support_tickets(current_user_id)
        
        ticket_list = []
        for ticket in support_tickets:
            ticket_list.append({
                "support_id": ticket.SupportID,
                "title": ticket.Title,
                "status": ticket.Status,
                "issue_description": ticket.Issue_des,
                "created_at": ticket.Create_at.isoformat(),
                "updated_at": ticket.Updated_at.isoformat() if ticket.Updated_at else None
            })
        
        return jsonify({
            "support_tickets": ticket_list,
            "count": len(ticket_list),
            "message": "Support tickets retrieved successfully"
        }), 200
        
    except ValueError as e:
        return jsonify({"message": str(e)}), 404
    except Exception as e:
        return jsonify({"message": "Error retrieving support tickets", "error": str(e)}), 500

@bp.route('/<int:support_id>', methods=['GET'])
@jwt_required()
def get_support_ticket(support_id):
    """
    Get support ticket by ID
    ---
    get:
      summary: Get support ticket by ID
      security:
        - BearerAuth: []
      parameters:
        - name: support_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Support
      responses:
        200:
          description: Support ticket retrieved successfully
        404:
          description: Support ticket not found
    """
    try:
        support = support_service.get_support_ticket(support_id)
        if not support:
            return jsonify({'message': 'Support ticket not found'}), 404
        
        return jsonify({
            "support_id": support.SupportID,
            "user_id": support.UserID,
            "title": support.Title,
            "status": support.Status,
            "issue_description": support.Issue_des,
            "created_at": support.Create_at.isoformat(),
            "updated_at": support.Updated_at.isoformat() if support.Updated_at else None,
            "message": "Support ticket retrieved successfully"
        }), 200
        
    except Exception as e:
        return jsonify({"message": "Error retrieving support ticket", "error": str(e)}), 500

@bp.route('/<int:support_id>', methods=['PUT'])
@jwt_required()
def update_support_ticket(support_id):
    """
    Update support ticket
    ---
    put:
      summary: Update support ticket
      security:
        - BearerAuth: []
      parameters:
        - name: support_id
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
                title:
                  type: string
                  maxLength: 200
                issue_description:
                  type: string
                  maxLength: 2000
                status:
                  type: string
                  enum: [open, in_progress, resolved, closed]
      tags:
        - Support
      responses:
        200:
          description: Support ticket updated successfully
        404:
          description: Support ticket not found
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "No data provided"}), 400
            
        errors = support_update_schema.validate(data)
        if errors:
            return jsonify({"message": "Validation errors", "errors": errors}), 400
        
        support = support_service.update_support_ticket(
            support_id=support_id,
            title=data.get('title'),
            issue_description=data.get('issue_description'),
            status=data.get('status')
        )
        
        if not support:
            return jsonify({'message': 'Support ticket not found'}), 404
        
        return jsonify({
            "support_id": support.SupportID,
            "title": support.Title,
            "status": support.Status,
            "issue_description": support.Issue_des,
            "updated_at": support.Updated_at.isoformat() if support.Updated_at else None,
            "message": "Support ticket updated successfully"
        }), 200
        
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": "Error updating support ticket", "error": str(e)}), 500

@bp.route('/<int:support_id>/status', methods=['PUT'])
@jwt_required()
def update_support_status(support_id):
    """
    Update support ticket status
    ---
    put:
      summary: Update support ticket status
      security:
        - BearerAuth: []
      parameters:
        - name: support_id
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
                  enum: [open, in_progress, resolved, closed]
              required:
                - status
      tags:
        - Support
      responses:
        200:
          description: Support ticket status updated successfully
        404:
          description: Support ticket not found
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "No data provided"}), 400
            
        errors = support_status_schema.validate(data)
        if errors:
            return jsonify({"message": "Validation errors", "errors": errors}), 400
        
        success = support_service.update_support_status(support_id, data['status'])
        if not success:
            return jsonify({'message': 'Support ticket not found'}), 404
        
        return jsonify({
            "support_id": support_id,
            "status": data['status'],
            "message": "Support ticket status updated successfully"
        }), 200
        
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": "Error updating support ticket status", "error": str(e)}), 500

@bp.route('/status/<status>', methods=['GET'])
@jwt_required()
def get_support_tickets_by_status(status):
    """
    Get support tickets by status (admin function)
    ---
    get:
      summary: Get support tickets by status
      security:
        - BearerAuth: []
      parameters:
        - name: status
          in: path
          required: true
          schema:
            type: string
            enum: [open, in_progress, resolved, closed]
      tags:
        - Support
      responses:
        200:
          description: Support tickets retrieved successfully
    """
    try:
        support_tickets = support_service.get_support_tickets_by_status(status)
        
        ticket_list = []
        for ticket in support_tickets:
            ticket_list.append({
                "support_id": ticket.SupportID,
                "user_id": ticket.UserID,
                "title": ticket.Title,
                "status": ticket.Status,
                "issue_description": ticket.Issue_des,
                "created_at": ticket.Create_at.isoformat(),
                "updated_at": ticket.Updated_at.isoformat() if ticket.Updated_at else None
            })
        
        return jsonify({
            "support_tickets": ticket_list,
            "status": status,
            "count": len(ticket_list),
            "message": "Support tickets retrieved successfully"
        }), 200
        
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": "Error retrieving support tickets", "error": str(e)}), 500
