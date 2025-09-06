from typing import List, Optional
from domain.models.message import Message
from domain.models.imessage_repository import IMessageRepository
from infrastructure.models.message_model import MessageModel
from datetime import datetime

class MessageRepository(IMessageRepository):
    def __init__(self, session=None):
        if session is None:
            from infrastructure.databases.mssql import session as default_session
            self.session = default_session
        else:
            self.session = session
    def add(self, message: Message) -> Message:
        model = MessageModel(
            SenderID=message.SenderID,
            ReceiverID=message.ReceiverID,
            Content=message.Content,
            TicketID=message.TicketID,
            IsRead=message.IsRead,
            SentAt=message.SentAt,
            ReadAt=message.ReadAt
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_domain(model)

    def get_by_id(self, message_id: int) -> Optional[Message]:
        model = self.session.query(MessageModel).filter(MessageModel.MessageID == message_id).first()
        return self._to_domain(model) if model else None

    def get_conversation(self, user1_id: int, user2_id: int, limit: int = 50, offset: int = 0) -> List[Message]:
        models = self.session.query(MessageModel).filter(
            ((MessageModel.SenderID == user1_id) & (MessageModel.ReceiverID == user2_id)) |
            ((MessageModel.SenderID == user2_id) & (MessageModel.ReceiverID == user1_id))
        ).order_by(MessageModel.SentAt.desc()).offset(offset).limit(limit).all()
        return [self._to_domain(model) for model in models]
    
    def get_user_conversations(self, user_id: int) -> List[dict]:
        # Get all unique conversations for a user
        conversations = self.session.query(MessageModel).filter(
            (MessageModel.SenderID == user_id) | (MessageModel.ReceiverID == user_id)
        ).order_by(MessageModel.SentAt.desc()).all()

        # Group by conversation partner
        conversation_dict = {}
        for msg in conversations:
            partner_id = msg.ReceiverID if msg.SenderID == user_id else msg.SenderID
            if partner_id not in conversation_dict:
                conversation_dict[partner_id] = {
                    'user_id': partner_id,
                    'last_message': msg.Content,
                    'last_message_time': msg.SentAt,
                    'unread_count': 0
                }

        # Count unread messages
        for partner_id in conversation_dict:
            unread_count = self.session.query(MessageModel).filter(
                (MessageModel.SenderID == partner_id) &
                (MessageModel.ReceiverID == user_id) &
                (MessageModel.IsRead == False)
            ).count()
            conversation_dict[partner_id]['unread_count'] = unread_count

        return list(conversation_dict.values())
    
    def mark_as_read(self, sender_id: int, receiver_id: int) -> bool:
        messages = self.session.query(MessageModel).filter(
            (MessageModel.SenderID == sender_id) &
            (MessageModel.ReceiverID == receiver_id) &
            (MessageModel.IsRead == False)
        ).all()

        for message in messages:
            message.IsRead = True
            message.ReadAt = datetime.now()

        self.session.commit()
        return True

    def get_unread_count(self, user_id: int) -> int:
        return self.session.query(MessageModel).filter(
            (MessageModel.ReceiverID == user_id) & (MessageModel.IsRead == False)
        ).count()

    def delete(self, message_id: int) -> bool:
        model = self.session.query(MessageModel).filter(MessageModel.MessageID == message_id).first()
        if model:
            self.session.delete(model)
            self.session.commit()
            return True
        return False
    
    def _to_domain(self, model: MessageModel) -> Message:
        return Message(
            MessageID=model.MessageID,
            SenderID=model.SenderID,
            ReceiverID=model.ReceiverID,
            Content=model.Content,
            TicketID=model.TicketID,
            IsRead=model.IsRead,
            SentAt=model.SentAt,
            ReadAt=model.ReadAt
        )

    def search_messages(self, user_id: int, query: str, other_user_id: Optional[int] = None, limit: int = 20, offset: int = 0) -> List[Message]:
        """Search messages by content"""
        query_filter = MessageModel.Content.ilike(f'%{query}%')

        # Base filter - user must be sender or receiver
        user_filter = (MessageModel.SenderID == user_id) | (MessageModel.ReceiverID == user_id)

        # If other_user_id specified, filter conversation
        if other_user_id:
            conversation_filter = (
                ((MessageModel.SenderID == user_id) & (MessageModel.ReceiverID == other_user_id)) |
                ((MessageModel.SenderID == other_user_id) & (MessageModel.ReceiverID == user_id))
            )
            user_filter = conversation_filter

        models = self.session.query(MessageModel).filter(
            query_filter & user_filter
        ).order_by(MessageModel.SentAt.desc()).offset(offset).limit(limit).all()

        return [self._to_domain(model) for model in models]

    def get_user_stats(self, user_id: int) -> dict:
        """Get chat statistics for a user"""
        from datetime import datetime, timedelta

        # Total messages sent
        messages_sent = self.session.query(MessageModel).filter(MessageModel.SenderID == user_id).count()

        # Total messages received
        messages_received = self.session.query(MessageModel).filter(MessageModel.ReceiverID == user_id).count()

        # Unread messages
        unread_messages = self.session.query(MessageModel).filter(
            (MessageModel.ReceiverID == user_id) & (MessageModel.IsRead == False)
        ).count()

        # Total conversations (unique users)
        sent_to = self.session.query(MessageModel.ReceiverID).filter(MessageModel.SenderID == user_id).distinct().all()
        received_from = self.session.query(MessageModel.SenderID).filter(MessageModel.ReceiverID == user_id).distinct().all()

        unique_users = set()
        for (user,) in sent_to:
            unique_users.add(user)
        for (user,) in received_from:
            unique_users.add(user)

        total_conversations = len(unique_users)

        # Active conversations (last 7 days)
        seven_days_ago = datetime.now() - timedelta(days=7)
        active_conversations_query = self.session.query(MessageModel).filter(
            ((MessageModel.SenderID == user_id) | (MessageModel.ReceiverID == user_id)) &
            (MessageModel.SentAt >= seven_days_ago)
        ).all()

        active_users = set()
        for msg in active_conversations_query:
            partner_id = msg.ReceiverID if msg.SenderID == user_id else msg.SenderID
            active_users.add(partner_id)

        active_conversations = len(active_users)

        return {
            "total_conversations": total_conversations,
            "total_messages_sent": messages_sent,
            "total_messages_received": messages_received,
            "unread_messages": unread_messages,
            "active_conversations": active_conversations
        }
