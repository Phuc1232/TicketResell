from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.jwt_helpers import get_current_user_id
from marshmallow import Schema, fields, validate
from datetime import datetime
from services.chat_service import ChatService
from infrastructure.repositories.message_repository import MessageRepository
from infrastructure.repositories.user_repository import UserRepository
from infrastructure.repositories.ticket_repository import TicketRepository
from infrastructure.databases.mssql import session

bp = Blueprint('chat', __name__, url_prefix='/api/chat')

# Initialize services
message_repository = MessageRepository(session)
user_repository = UserRepository(session)
ticket_repository = TicketRepository(session)
chat_service = ChatService(message_repository, user_repository, ticket_repository)

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

        current_user_id = get_current_user_id()
        receiver_id = data['receiver_id']
        content = data['content']
        ticket_id = data.get('ticket_id')

        # Use ChatService to send message
        message = chat_service.send_message(
            sender_id=current_user_id,
            receiver_id=receiver_id,
            content=content,
            ticket_id=ticket_id
        )

        return jsonify({
            "message_id": message.MessageID,
            "content": message.Content,
            "sender_id": message.SenderID,
            "receiver_id": message.ReceiverID,
            "ticket_id": message.TicketID,
            "sent_at": message.SentAt.isoformat(),
            "message": "Message sent successfully"
        }), 201

    except ValueError as e:
        return jsonify({"message": str(e)}), 404
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
        current_user_id = get_current_user_id()
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)

        # Use ChatService to get conversation
        messages = chat_service.get_conversation(
            user1_id=current_user_id,
            user2_id=other_user_id,
            limit=limit,
            offset=offset
        )

        # Convert to response format
        message_list = []
        for msg in messages:
            message_list.append({
                "message_id": msg.MessageID,
                "content": msg.Content,
                "sender_id": msg.SenderID,
                "receiver_id": msg.ReceiverID,
                "ticket_id": msg.TicketID,
                "is_read": msg.IsRead,
                "sent_at": msg.SentAt.isoformat(),
                "read_at": msg.ReadAt.isoformat() if msg.ReadAt else None
            })

        return jsonify({
            "messages": message_list,
            "total": len(message_list),
            "limit": limit,
            "offset": offset,
            "message": "Messages retrieved successfully"
        }), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 404
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
        current_user_id = get_current_user_id()

        # Use ChatService to get user conversations
        conversations = chat_service.get_user_conversations(current_user_id)

        # Convert to response format
        conversation_list = []
        for conv in conversations:
            # Get username for the conversation partner
            partner = user_repository.get_by_id(conv['user_id'])
            username = partner.username if partner else f"User_{conv['user_id']}"

            conversation_list.append({
                "user_id": conv['user_id'],
                "username": username,
                "last_message": conv['last_message'],
                "last_message_time": conv['last_message_time'].isoformat(),
                "unread_count": conv['unread_count']
            })

        return jsonify({
            "conversations": conversation_list,
            "message": "Conversations retrieved successfully"
        }), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 404
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
        current_user_id = get_current_user_id()

        # Use ChatService to mark messages as read
        success = chat_service.mark_messages_as_read(
            sender_id=other_user_id,
            receiver_id=current_user_id
        )

        if success:
            return jsonify({
                "message": "Messages marked as read successfully",
                "user_id": other_user_id
            }), 200
        else:
            return jsonify({
                "message": "Failed to mark messages as read"
            }), 500

    except ValueError as e:
        return jsonify({"message": str(e)}), 404
    except Exception as e:
        return jsonify({"message": "Error marking messages as read", "error": str(e)}), 500

@bp.route('/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    """
    Get unread messages count
    ---
    get:
      summary: Get total unread messages count for current user
      security:
        - BearerAuth: []
      tags:
        - Chat
      responses:
        200:
          description: Unread count retrieved successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  unread_count:
                    type: integer
                  message:
                    type: string
    """
    try:
        current_user_id = get_current_user_id()

        unread_count = chat_service.get_unread_count(current_user_id)

        return jsonify({
            "unread_count": unread_count,
            "message": "Unread count retrieved successfully"
        }), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 404
    except Exception as e:
        return jsonify({"message": "Error retrieving unread count", "error": str(e)}), 500

@bp.route('/messages/<int:message_id>', methods=['DELETE'])
@jwt_required()
def delete_message(message_id):
    """
    Delete a message
    ---
    delete:
      summary: Delete a message (only sender can delete)
      security:
        - BearerAuth: []
      parameters:
        - name: message_id
          in: path
          required: true
          schema:
            type: integer
          description: ID of the message to delete
      tags:
        - Chat
      responses:
        200:
          description: Message deleted successfully
        403:
          description: Access denied - not message owner
        404:
          description: Message not found
    """
    try:
        current_user_id = get_current_user_id()

        success = chat_service.delete_message(message_id, current_user_id)

        if success:
            return jsonify({
                "message": "Message deleted successfully",
                "message_id": message_id
            }), 200
        else:
            return jsonify({
                "message": "Failed to delete message"
            }), 500

    except ValueError as e:
        error_msg = str(e)
        if "access denied" in error_msg.lower():
            return jsonify({"message": error_msg}), 403
        return jsonify({"message": error_msg}), 404
    except Exception as e:
        return jsonify({"message": "Error deleting message", "error": str(e)}), 500

@bp.route('/search', methods=['GET'])
@jwt_required()
def search_messages():
    """
    Search messages
    ---
    get:
      summary: Search messages by content
      security:
        - BearerAuth: []
      parameters:
        - name: query
          in: query
          required: true
          schema:
            type: string
            minLength: 1
          description: Search query
        - name: other_user_id
          in: query
          schema:
            type: integer
          description: Optional - search only in conversation with specific user
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
          description: Number of results to return
        - name: offset
          in: query
          schema:
            type: integer
            default: 0
          description: Number of results to skip
      tags:
        - Chat
      responses:
        200:
          description: Search results retrieved successfully
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
        400:
          description: Invalid search query
    """
    try:
        current_user_id = get_current_user_id()
        query = request.args.get('query', '').strip()
        other_user_id = request.args.get('other_user_id', type=int)
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)

        if not query:
            return jsonify({"message": "Search query is required"}), 400

        if len(query) < 1:
            return jsonify({"message": "Search query must be at least 1 character"}), 400

        # Use ChatService to search messages
        messages = chat_service.search_messages(
            user_id=current_user_id,
            query=query,
            other_user_id=other_user_id,
            limit=limit,
            offset=offset
        )

        # Convert to response format
        message_list = []
        for msg in messages:
            message_list.append({
                "message_id": msg.MessageID,
                "content": msg.Content,
                "sender_id": msg.SenderID,
                "receiver_id": msg.ReceiverID,
                "ticket_id": msg.TicketID,
                "sent_at": msg.SentAt.isoformat(),
                "is_read": msg.IsRead
            })

        return jsonify({
            "messages": message_list,
            "total": len(message_list),
            "query": query,
            "limit": limit,
            "offset": offset,
            "message": "Search results retrieved successfully"
        }), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 404
    except Exception as e:
        return jsonify({"message": "Error searching messages", "error": str(e)}), 500

@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_chat_stats():
    """
    Get chat statistics
    ---
    get:
      summary: Get chat statistics for current user
      security:
        - BearerAuth: []
      tags:
        - Chat
      responses:
        200:
          description: Chat statistics retrieved successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  total_conversations:
                    type: integer
                  total_messages_sent:
                    type: integer
                  total_messages_received:
                    type: integer
                  unread_messages:
                    type: integer
                  active_conversations:
                    type: integer
                    description: Conversations with messages in last 7 days
    """
    try:
        current_user_id = get_current_user_id()

        # Get chat statistics
        stats = chat_service.get_user_chat_stats(current_user_id)

        return jsonify({
            **stats,
            "message": "Chat statistics retrieved successfully"
        }), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 404
    except Exception as e:
        return jsonify({"message": "Error retrieving chat statistics", "error": str(e)}), 500
