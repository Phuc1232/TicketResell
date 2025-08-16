from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, validate
from datetime import datetime

bp = Blueprint('chat', __name__, url_prefix='/api/chat')

# Schemas
class MessageSchema(Schema):
    receiver_id = fields.Int(required=True, validate=validate.Range(min=1),
                            error_messages={"required": "Receiver ID is required",
                                           "validator_failed": "Receiver ID must be a positive integer"})
    content = fields.Str(required=True, validate=validate.Length(min=1, max=1000),
                        error_messages={"required": "Message content is required",
                                       "validator_failed": "Message content must be between 1 and 1000 characters"})
    ticket_id = fields.Int(validate=validate.Range(min=1))

class ChatRoomSchema(Schema):
    other_user_id = fields.Int(required=True, validate=validate.Range(min=1))

message_schema = MessageSchema()
chat_room_schema = ChatRoomSchema()

@bp.route('/send', methods=['POST'])
@jwt_required()
def send_message():
    """
    Send a message to another user
    ---
    post:
      summary: Send a message to another user
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                receiver_id:
                  type: integer
                  description: ID of the user to send message to
                content:
                  type: string
                  description: Message content
                ticket_id:
                  type: integer
                  description: Optional ticket ID if message is related to a ticket
              required:
                - receiver_id
                - content
      tags:
        - Chat
      responses:
        201:
          description: Message sent successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  message_id:
                    type: integer
                  content:
                    type: string
                  sender_id:
                    type: integer
                  receiver_id:
                    type: integer
                  sent_at:
                    type: string
                    format: date-time
        400:
          description: Invalid input data
        404:
          description: Receiver not found
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "No data provided"}), 400
            
        errors = message_schema.validate(data)
        if errors:
            return jsonify({"message": "Validation errors", "errors": errors}), 400
        
        current_user_id = int(get_jwt_identity())
        receiver_id = data['receiver_id']
        content = data['content']
        ticket_id = data.get('ticket_id')
        
        # TODO: Implement message service logic
        # 1. Validate receiver exists
        # 2. Create message record
        # 3. Send push notification to receiver
        # 4. Return message details
        
        return jsonify({
            "message_id": 1,
            "content": content,
            "sender_id": current_user_id,
            "receiver_id": receiver_id,
            "ticket_id": ticket_id,
            "sent_at": datetime.now().isoformat(),
            "message": "Message sent successfully"
        }), 201
        
    except Exception as e:
        return jsonify({"message": "Error sending message", "error": str(e)}), 500

@bp.route('/messages/<int:other_user_id>', methods=['GET'])
@jwt_required()
def get_messages(other_user_id):
    """
    Get chat messages with another user
    ---
    get:
      summary: Get chat messages with another user
      security:
        - BearerAuth: []
      parameters:
        - name: other_user_id
          in: path
          required: true
          schema:
            type: integer
          description: ID of the other user in the conversation
        - name: limit
          in: query
          schema:
            type: integer
            default: 50
          description: Number of messages to retrieve
        - name: offset
          in: query
          schema:
            type: integer
            default: 0
          description: Number of messages to skip
      tags:
        - Chat
      responses:
        200:
          description: Messages retrieved successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  messages:
                    type: array
                    items:
                      type: object
                      properties:
                        message_id:
                          type: integer
                        content:
                          type: string
                        sender_id:
                          type: integer
                        receiver_id:
                          type: integer
                        sent_at:
                          type: string
                          format: date-time
                  total:
                    type: integer
        404:
          description: User not found
    """
    try:
        current_user_id = int(get_jwt_identity())
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # TODO: Implement message retrieval logic
        # 1. Validate other user exists
        # 2. Get messages between current user and other user
        # 3. Apply pagination
        # 4. Mark messages as read
        
        messages = [
            {
                "message_id": 1,
                "content": "Hello, is this ticket still available?",
                "sender_id": other_user_id,
                "receiver_id": current_user_id,
                "sent_at": datetime.now().isoformat()
            },
            {
                "message_id": 2,
                "content": "Yes, it's still available!",
                "sender_id": current_user_id,
                "receiver_id": other_user_id,
                "sent_at": datetime.now().isoformat()
            }
        ]
        
        return jsonify({
            "messages": messages,
            "total": len(messages),
            "limit": limit,
            "offset": offset,
            "message": "Messages retrieved successfully"
        }), 200
        
    except Exception as e:
        return jsonify({"message": "Error retrieving messages", "error": str(e)}), 500

@bp.route('/conversations', methods=['GET'])
@jwt_required()
def get_conversations():
    """
    Get list of conversations
    ---
    get:
      summary: Get list of conversations for current user
      security:
        - BearerAuth: []
      tags:
        - Chat
      responses:
        200:
          description: Conversations retrieved successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  conversations:
                    type: array
                    items:
                      type: object
                      properties:
                        user_id:
                          type: integer
                        username:
                          type: string
                        last_message:
                          type: string
                        last_message_time:
                          type: string
                          format: date-time
                        unread_count:
                          type: integer
    """
    try:
        current_user_id = int(get_jwt_identity())
        
        # TODO: Implement conversation list logic
        # 1. Get all users that current user has conversations with
        # 2. Get last message for each conversation
        # 3. Get unread message count
        
        conversations = [
            {
                "user_id": 2,
                "username": "john_doe",
                "last_message": "Is this ticket still available?",
                "last_message_time": datetime.now().isoformat(),
                "unread_count": 1
            },
            {
                "user_id": 3,
                "username": "jane_smith",
                "last_message": "Thanks for the ticket!",
                "last_message_time": datetime.now().isoformat(),
                "unread_count": 0
            }
        ]
        
        return jsonify({
            "conversations": conversations,
            "message": "Conversations retrieved successfully"
        }), 200
        
    except Exception as e:
        return jsonify({"message": "Error retrieving conversations", "error": str(e)}), 500

@bp.route('/mark-read/<int:other_user_id>', methods=['POST'])
@jwt_required()
def mark_messages_read(other_user_id):
    """
    Mark messages as read
    ---
    post:
      summary: Mark messages from a specific user as read
      security:
        - BearerAuth: []
      parameters:
        - name: other_user_id
          in: path
          required: true
          schema:
            type: integer
          description: ID of the user whose messages to mark as read
      tags:
        - Chat
      responses:
        200:
          description: Messages marked as read successfully
    """
    try:
        current_user_id = int(get_jwt_identity())
        
        # TODO: Implement mark as read logic
        # 1. Update all unread messages from other_user_id to current_user_id
        # 2. Return success response
        
        return jsonify({
            "message": "Messages marked as read successfully",
            "user_id": other_user_id
        }), 200
        
    except Exception as e:
        return jsonify({"message": "Error marking messages as read", "error": str(e)}), 500
