from typing import List, Optional
from domain.models.message import Message
from domain.models.imessage_repository import IMessageRepository
from domain.models.iuser_repository import IUserRepository
from domain.models.itticket_repository import ITicketRepository
from datetime import datetime

class ChatService:
    def __init__(self, message_repository: IMessageRepository, user_repository: IUserRepository, ticket_repository: ITicketRepository):
        self.message_repository = message_repository
        self.user_repository = user_repository
        self.ticket_repository = ticket_repository
    
    def send_message(self, sender_id: int, receiver_id: int, content: str, ticket_id: Optional[int] = None) -> Message:
        # Validate sender exists
        sender = self.user_repository.get_by_id(sender_id)
        if not sender:
            raise ValueError("Sender not found")
        
        # Validate receiver exists
        receiver = self.user_repository.get_by_id(receiver_id)
        if not receiver:
            raise ValueError("Receiver not found")
        
        # Validate ticket exists if provided
        if ticket_id:
            ticket = self.ticket_repository.get_by_id(ticket_id)
            if not ticket:
                raise ValueError("Ticket not found")
        
        # Create message
        message = Message(
            MessageID=None,
            SenderID=sender_id,
            ReceiverID=receiver_id,
            Content=content,
            TicketID=ticket_id,
            IsRead=False,
            SentAt=datetime.now(),
            ReadAt=None
        )
        
        return self.message_repository.add(message)
    
    def get_conversation(self, user1_id: int, user2_id: int, limit: int = 50, offset: int = 0) -> List[Message]:
        # Validate both users exist
        user1 = self.user_repository.get_by_id(user1_id)
        user2 = self.user_repository.get_by_id(user2_id)
        if not user1 or not user2:
            raise ValueError("User not found")
        
        return self.message_repository.get_conversation(user1_id, user2_id, limit, offset)
    
    def get_user_conversations(self, user_id: int) -> List[dict]:
        # Validate user exists
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        return self.message_repository.get_user_conversations(user_id)
    
    def mark_messages_as_read(self, sender_id: int, receiver_id: int) -> bool:
        # Validate both users exist
        sender = self.user_repository.get_by_id(sender_id)
        receiver = self.user_repository.get_by_id(receiver_id)
        if not sender or not receiver:
            raise ValueError("User not found")
        
        return self.message_repository.mark_as_read(sender_id, receiver_id)
    
    def get_unread_count(self, user_id: int) -> int:
        # Validate user exists
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        return self.message_repository.get_unread_count(user_id)
    
    def delete_message(self, message_id: int, user_id: int) -> bool:
        # Validate user exists
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Check if user owns the message
        message = self.message_repository.get_by_id(message_id)
        if not message or message.SenderID != user_id:
            raise ValueError("Message not found or access denied")
        
        return self.message_repository.delete(message_id)

    def search_messages(self, user_id: int, query: str, other_user_id: Optional[int] = None, limit: int = 20, offset: int = 0) -> List[Message]:
        """Search messages by content for a specific user"""
        # Validate user exists
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        # Validate other user if provided
        if other_user_id:
            other_user = self.user_repository.get_by_id(other_user_id)
            if not other_user:
                raise ValueError("Other user not found")

        return self.message_repository.search_messages(user_id, query, other_user_id, limit, offset)

    def get_user_chat_stats(self, user_id: int) -> dict:
        """Get chat statistics for a user"""
        # Validate user exists
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        return self.message_repository.get_user_stats(user_id)

    def get_message_by_id(self, message_id: int, user_id: int) -> Optional[Message]:
        """Get a specific message if user has access to it"""
        # Validate user exists
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        message = self.message_repository.get_by_id(message_id)
        if not message:
            return None

        # Check if user has access to this message
        if message.SenderID != user_id and message.ReceiverID != user_id:
            raise ValueError("Access denied")

        return message
