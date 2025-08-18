from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.jwt_helpers import get_current_user_id
from marshmallow import Schema, fields, validate
from datetime import datetime

bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')

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
