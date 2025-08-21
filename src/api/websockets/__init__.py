"""
WebSocket module for real-time features
"""

from .chat_websocket import init_chat_websocket, get_active_users, is_user_online

__all__ = ['init_chat_websocket', 'get_active_users', 'is_user_online']
