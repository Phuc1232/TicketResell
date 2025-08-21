from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
from flask_jwt_extended import decode_token
from functools import wraps
import logging
from services.chat_service import ChatService
from infrastructure.repositories.message_repository import MessageRepository
from infrastructure.repositories.user_repository import UserRepository
from infrastructure.repositories.ticket_repository import TicketRepository
from infrastructure.databases.mssql import session

# Initialize services
message_repository = MessageRepository(session)
user_repository = UserRepository(session)
ticket_repository = TicketRepository(session)
chat_service = ChatService(message_repository, user_repository, ticket_repository)

# Store active connections
active_connections = {}

def authenticated_only(f):
    """Decorator to require authentication for WebSocket events"""
    @wraps(f)
    def wrapped(*args, **kwargs):
        try:
            # Get token from client
            token = kwargs.get('token') or (args[0].get('token') if args else None)
            if not token:
                emit('error', {'message': 'Authentication token required'})
                disconnect()
                return
            
            # Decode JWT token
            decoded_token = decode_token(token)
            user_id = decoded_token['sub']
            
            # Add user_id to kwargs
            kwargs['user_id'] = user_id
            return f(*args, **kwargs)
            
        except Exception as e:
            logging.error(f"WebSocket authentication error: {str(e)}")
            emit('error', {'message': 'Invalid authentication token'})
            disconnect()
    return wrapped

def init_chat_websocket(socketio: SocketIO):
    """Initialize chat WebSocket events"""
    
    @socketio.on('connect', namespace='/chat')
    def on_connect():
        """Handle client connection"""
        logging.info(f"Client connected: {request.sid}")
        emit('connected', {'message': 'Connected to chat server'})
    
    @socketio.on('disconnect', namespace='/chat')
    def on_disconnect():
        """Handle client disconnection"""
        if request.sid in active_connections:
            user_id = active_connections[request.sid]
            leave_room(f"user_{user_id}", namespace='/chat')
            del active_connections[request.sid]
        logging.info(f"Client disconnected: {request.sid}")
    
    @socketio.on('join', namespace='/chat')
    @authenticated_only
    def on_join(data, user_id):
        """Join user's personal room for receiving messages"""
        try:
            # Join user's personal room
            join_room(f"user_{user_id}", namespace='/chat')
            active_connections[request.sid] = user_id
            
            emit('joined', {
                'message': f'Joined chat room for user {user_id}',
                'user_id': user_id
            })
            
            # Send unread count
            unread_count = chat_service.get_unread_count(user_id)
            emit('unread_count', {'count': unread_count})
            
        except Exception as e:
            logging.error(f"Error joining chat room: {str(e)}")
            emit('error', {'message': 'Failed to join chat room'})
    
    @socketio.on('send_message', namespace='/chat')
    @authenticated_only
    def on_send_message(data, user_id):
        """Handle sending a message"""
        try:
            receiver_id = data.get('receiver_id')
            content = data.get('content')
            ticket_id = data.get('ticket_id')
            
            if not receiver_id or not content:
                emit('error', {'message': 'receiver_id and content are required'})
                return
            
            # Send message using chat service
            message = chat_service.send_message(
                sender_id=user_id,
                receiver_id=receiver_id,
                content=content,
                ticket_id=ticket_id
            )
            
            # Prepare message data
            message_data = {
                'message_id': message.MessageID,
                'sender_id': message.SenderID,
                'receiver_id': message.ReceiverID,
                'content': message.Content,
                'ticket_id': message.TicketID,
                'sent_at': message.SentAt.isoformat(),
                'is_read': message.IsRead
            }
            
            # Send to sender (confirmation)
            emit('message_sent', message_data)
            
            # Send to receiver (if online)
            socketio.emit('new_message', message_data, 
                         room=f"user_{receiver_id}", namespace='/chat')
            
            # Update unread count for receiver
            unread_count = chat_service.get_unread_count(receiver_id)
            socketio.emit('unread_count', {'count': unread_count}, 
                         room=f"user_{receiver_id}", namespace='/chat')
            
        except ValueError as e:
            emit('error', {'message': str(e)})
        except Exception as e:
            logging.error(f"Error sending message: {str(e)}")
            emit('error', {'message': 'Failed to send message'})
    
    @socketio.on('mark_read', namespace='/chat')
    @authenticated_only
    def on_mark_read(data, user_id):
        """Mark messages as read"""
        try:
            sender_id = data.get('sender_id')
            
            if not sender_id:
                emit('error', {'message': 'sender_id is required'})
                return
            
            # Mark messages as read
            success = chat_service.mark_messages_as_read(sender_id, user_id)
            
            if success:
                emit('messages_marked_read', {
                    'sender_id': sender_id,
                    'message': 'Messages marked as read'
                })
                
                # Update unread count
                unread_count = chat_service.get_unread_count(user_id)
                emit('unread_count', {'count': unread_count})
            else:
                emit('error', {'message': 'Failed to mark messages as read'})
                
        except ValueError as e:
            emit('error', {'message': str(e)})
        except Exception as e:
            logging.error(f"Error marking messages as read: {str(e)}")
            emit('error', {'message': 'Failed to mark messages as read'})
    
    @socketio.on('typing', namespace='/chat')
    @authenticated_only
    def on_typing(data, user_id):
        """Handle typing indicator"""
        try:
            receiver_id = data.get('receiver_id')
            is_typing = data.get('is_typing', False)
            
            if not receiver_id:
                emit('error', {'message': 'receiver_id is required'})
                return
            
            # Send typing indicator to receiver
            socketio.emit('user_typing', {
                'user_id': user_id,
                'is_typing': is_typing
            }, room=f"user_{receiver_id}", namespace='/chat')
            
        except Exception as e:
            logging.error(f"Error handling typing indicator: {str(e)}")
            emit('error', {'message': 'Failed to send typing indicator'})
    
    @socketio.on('get_online_status', namespace='/chat')
    @authenticated_only
    def on_get_online_status(data, user_id):
        """Get online status of users"""
        try:
            user_ids = data.get('user_ids', [])
            
            online_status = {}
            for uid in user_ids:
                # Check if user has active connection
                is_online = any(active_user_id == uid for active_user_id in active_connections.values())
                online_status[uid] = is_online
            
            emit('online_status', online_status)
            
        except Exception as e:
            logging.error(f"Error getting online status: {str(e)}")
            emit('error', {'message': 'Failed to get online status'})

def get_active_users():
    """Get list of currently active users"""
    return list(set(active_connections.values()))

def is_user_online(user_id: int) -> bool:
    """Check if a specific user is online"""
    return user_id in active_connections.values()
