from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.jwt_helpers import get_current_user_id
from marshmallow import Schema, fields, validate
from datetime import datetime
from services.notification_service import NotificationService
from infrastructure.repositories.notification_repository import NotificationRepository
from infrastructure.repositories.user_repository import UserRepository
from infrastructure.databases.mssql import session
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')

# Initialize services
notification_repository = NotificationRepository(session)
user_repository = UserRepository(session)
notification_service = NotificationService(notification_repository, user_repository)

# Schemas
class NotificationPreferencesSchema(Schema):
    email_notifications = fields.Bool(load_default=True)
    push_notifications = fields.Bool(load_default=True)
    ticket_reminders = fields.Bool(load_default=True)
    price_alerts = fields.Bool(load_default=True)
    chat_notifications = fields.Bool(load_default=True)

notification_preferences_schema = NotificationPreferencesSchema()

@bp.route('/', methods=['GET'])
@jwt_required()
def get_notifications():
    """
    Get user notifications
    ---
    get:
      summary: Get notifications for current user
      security:
        - BearerAuth: []
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
          description: Number of notifications to retrieve
        - name: offset
          in: query
          schema:
            type: integer
            default: 0
          description: Number of notifications to skip
        - name: unread_only
          in: query
          schema:
            type: boolean
            default: false
          description: Return only unread notifications
      tags:
        - Notifications
      responses:
        200:
          description: Notifications retrieved successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  notifications:
                    type: array
                    items:
                      type: object
                      properties:
                        notification_id:
                          type: integer
                        title:
                          type: string
                        content:
                          type: string
                        type:
                          type: string
                          enum: [ticket_reminder, price_alert, chat_message, payment_confirmation, system]
                        is_read:
                          type: boolean
                        created_at:
                          type: string
                          format: date-time
                  total:
                    type: integer
                  unread_count:
                    type: integer
    """
    try:
        current_user_id = get_current_user_id()
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        unread_only = request.args.get('unread_only', False, type=bool)
        
        # TODO: Implement notification retrieval logic
        # 1. Get notifications for current user
        # 2. Apply filters (unread_only)
        # 3. Apply pagination
        # 4. Return notifications with metadata
        
        notifications = [
            {
                "notification_id": 1,
                "title": "Ticket Reminder",
                "content": "Your ticket for 'Concert XYZ' expires in 2 days",
                "type": "ticket_reminder",
                "is_read": False,
                "created_at": datetime.now().isoformat()
            },
            {
                "notification_id": 2,
                "title": "New Message",
                "content": "You have a new message from john_doe",
                "type": "chat_message",
                "is_read": True,
                "created_at": datetime.now().isoformat()
            },
            {
                "notification_id": 3,
                "title": "Price Alert",
                "content": "A ticket matching your search criteria is now available",
                "type": "price_alert",
                "is_read": False,
                "created_at": datetime.now().isoformat()
            }
        ]
        
        # Filter unread notifications if requested
        if unread_only:
            notifications = [n for n in notifications if not n['is_read']]
        
        unread_count = len([n for n in notifications if not n['is_read']])
        
        return jsonify({
            "notifications": notifications,
            "total": len(notifications),
            "unread_count": unread_count,
            "limit": limit,
            "offset": offset,
            "message": "Notifications retrieved successfully"
        }), 200
        
    except Exception as e:
        return jsonify({"message": "Error retrieving notifications", "error": str(e)}), 500

@bp.route('/<int:notification_id>/read', methods=['POST'])
@jwt_required()
def mark_notification_read(notification_id):
    """
    Mark notification as read
    ---
    post:
      summary: Mark a specific notification as read
      security:
        - BearerAuth: []
      parameters:
        - name: notification_id
          in: path
          required: true
          schema:
            type: integer
          description: ID of the notification to mark as read
      tags:
        - Notifications
      responses:
        200:
          description: Notification marked as read successfully
        404:
          description: Notification not found
    """
    try:
        current_user_id = get_current_user_id()
        
        # TODO: Implement mark as read logic
        # 1. Verify notification belongs to current user
        # 2. Update notification status to read
        # 3. Return success response
        
        return jsonify({
            "message": "Notification marked as read successfully",
            "notification_id": notification_id
        }), 200
        
    except Exception as e:
        return jsonify({"message": "Error marking notification as read", "error": str(e)}), 500

@bp.route('/read-all', methods=['POST'])
@jwt_required()
def mark_all_notifications_read():
    """
    Mark all notifications as read
    ---
    post:
      summary: Mark all notifications for current user as read
      security:
        - BearerAuth: []
      tags:
        - Notifications
      responses:
        200:
          description: All notifications marked as read successfully
    """
    try:
        current_user_id = get_current_user_id()
        
        # TODO: Implement mark all as read logic
        # 1. Update all unread notifications for current user
        # 2. Return success response
        
        return jsonify({
            "message": "All notifications marked as read successfully",
            "user_id": current_user_id
        }), 200
        
    except Exception as e:
        return jsonify({"message": "Error marking notifications as read", "error": str(e)}), 500

@bp.route('/preferences', methods=['GET'])
@jwt_required()
def get_notification_preferences():
    """
    Get notification preferences
    ---
    get:
      summary: Get notification preferences for current user
      security:
        - BearerAuth: []
      tags:
        - Notifications
      responses:
        200:
          description: Notification preferences retrieved successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  email_notifications:
                    type: boolean
                  push_notifications:
                    type: boolean
                  ticket_reminders:
                    type: boolean
                  price_alerts:
                    type: boolean
                  chat_notifications:
                    type: boolean
    """
    try:
        current_user_id = get_current_user_id()
        
        # TODO: Implement preferences retrieval logic
        # 1. Get notification preferences for current user
        # 2. Return preferences
        
        preferences = {
            "email_notifications": True,
            "push_notifications": True,
            "ticket_reminders": True,
            "price_alerts": True,
            "chat_notifications": True
        }
        
        return jsonify({
            **preferences,
            "message": "Notification preferences retrieved successfully"
        }), 200
        
    except Exception as e:
        return jsonify({"message": "Error retrieving notification preferences", "error": str(e)}), 500

@bp.route('/preferences', methods=['PUT'])
@jwt_required()
def update_notification_preferences():
    """
    Update notification preferences
    ---
    put:
      summary: Update notification preferences for current user
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                email_notifications:
                  type: boolean
                push_notifications:
                  type: boolean
                ticket_reminders:
                  type: boolean
                price_alerts:
                  type: boolean
                chat_notifications:
                  type: boolean
      tags:
        - Notifications
      responses:
        200:
          description: Notification preferences updated successfully
        400:
          description: Invalid input data
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "No data provided"}), 400
            
        errors = notification_preferences_schema.validate(data)
        if errors:
            return jsonify({"message": "Validation errors", "errors": errors}), 400
        
        current_user_id = get_current_user_id()
        
        # TODO: Implement preferences update logic
        # 1. Update notification preferences for current user
        # 2. Return updated preferences
        
        updated_preferences = {
            "email_notifications": data.get('email_notifications', True),
            "push_notifications": data.get('push_notifications', True),
            "ticket_reminders": data.get('ticket_reminders', True),
            "price_alerts": data.get('price_alerts', True),
            "chat_notifications": data.get('chat_notifications', True)
        }
        
        return jsonify({
            **updated_preferences,
            "message": "Notification preferences updated successfully"
        }), 200
        
    except Exception as e:
        return jsonify({"message": "Error updating notification preferences", "error": str(e)}), 500


@bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_notification_statistics():
    """
    Get notification statistics for current user
    ---
    get:
      summary: Get notification statistics
      security:
        - BearerAuth: []
      tags:
        - Notifications
      responses:
        200:
          description: Notification statistics retrieved successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  user_id:
                    type: integer
                  total_notifications:
                    type: integer
                  unread_count:
                    type: integer
                  read_count:
                    type: integer
                  type_breakdown:
                    type: object
                  recent_activity_count:
                    type: integer
                  read_percentage:
                    type: number
    """
    try:
        current_user_id = get_current_user_id()

        stats = notification_service.get_notification_statistics(current_user_id)

        return jsonify({
            **stats,
            "message": "Notification statistics retrieved successfully"
        }), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 404
    except Exception as e:
        logger.error(f"Error retrieving notification statistics: {e}")
        return jsonify({"message": "Error retrieving notification statistics", "error": str(e)}), 500


@bp.route('/type/<notification_type>', methods=['GET'])
@jwt_required()
def get_notifications_by_type(notification_type):
    """
    Get notifications of specific type for current user
    ---
    get:
      summary: Get notifications by type
      security:
        - BearerAuth: []
      parameters:
        - name: notification_type
          in: path
          required: true
          schema:
            type: string
            enum: [ticket_reminder, price_alert, chat_message, payment_confirmation, system]
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
        - Notifications
      responses:
        200:
          description: Notifications retrieved successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  notifications:
                    type: array
                    items:
                      type: object
                  total_count:
                    type: integer
                  limit:
                    type: integer
                  offset:
                    type: integer
        400:
          description: Invalid notification type
    """
    try:
        current_user_id = get_current_user_id()

        limit = min(int(request.args.get('limit', 20)), 100)
        offset = max(int(request.args.get('offset', 0)), 0)

        # Validate notification type
        valid_types = ['ticket_reminder', 'price_alert', 'chat_message', 'payment_confirmation', 'system']
        if notification_type not in valid_types:
            return jsonify({
                "message": f"Invalid notification type. Must be one of: {valid_types}"
            }), 400

        notifications = notification_service.get_notifications_by_type(
            current_user_id, notification_type, limit, offset
        )

        notification_list = []
        for notification in notifications:
            notification_list.append({
                "notification_id": notification.NotificationID,
                "title": notification.Title,
                "content": notification.Content,
                "type": notification.Type,
                "is_read": notification.IsRead,
                "created_at": notification.CreatedAt.isoformat(),
                "read_at": notification.ReadAt.isoformat() if notification.ReadAt else None
            })

        return jsonify({
            "notifications": notification_list,
            "total_count": len(notification_list),
            "limit": limit,
            "offset": offset,
            "notification_type": notification_type,
            "message": f"Notifications of type '{notification_type}' retrieved successfully"
        }), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 404
    except Exception as e:
        logger.error(f"Error retrieving notifications by type: {e}")
        return jsonify({"message": "Error retrieving notifications", "error": str(e)}), 500


@bp.route('/bulk-create', methods=['POST'])
@jwt_required()
def bulk_create_notifications():
    """
    Create multiple notifications (Admin only)
    ---
    post:
      summary: Create multiple notifications at once
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                notifications:
                  type: array
                  items:
                    type: object
                    properties:
                      user_id:
                        type: integer
                      title:
                        type: string
                      content:
                        type: string
                      type:
                        type: string
                        enum: [ticket_reminder, price_alert, chat_message, payment_confirmation, system]
                    required:
                      - user_id
                      - title
                      - content
                      - type
              required:
                - notifications
      tags:
        - Notifications
      responses:
        201:
          description: Notifications created successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  created_count:
                    type: integer
                  failed_count:
                    type: integer
                  message:
                    type: string
        400:
          description: Invalid input data
        403:
          description: Admin access required
    """
    try:
        # Check if user is admin (you might want to add admin_required decorator)
        from utils.jwt_helpers import get_current_user_role
        from api.decorators.auth_decorators import Roles

        current_role = get_current_user_role()
        if current_role != Roles.ADMIN:
            return jsonify({"message": "Admin access required"}), 403

        data = request.get_json()
        if not data or 'notifications' not in data:
            return jsonify({"message": "Notifications data is required"}), 400

        notifications_data = data['notifications']
        if not isinstance(notifications_data, list):
            return jsonify({"message": "Notifications must be a list"}), 400

        created_notifications = notification_service.bulk_create_notifications(notifications_data)

        return jsonify({
            "created_count": len(created_notifications),
            "failed_count": len(notifications_data) - len(created_notifications),
            "message": f"Successfully created {len(created_notifications)} notifications"
        }), 201

    except Exception as e:
        logger.error(f"Error bulk creating notifications: {e}")
        return jsonify({"message": "Error creating notifications", "error": str(e)}), 500
