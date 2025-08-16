from typing import List, Optional
from domain.models.message import Message
from domain.models.imessage_repository import IMessageRepository
from infrastructure.models.message_model import MessageModel
from infrastructure.databases.mssql import session
from datetime import datetime

class MessageRepository(IMessageRepository):
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
        session.add(model)
        session.commit()
        session.refresh(model)
        return self._to_domain(model)
    
    def get_by_id(self, message_id: int) -> Optional[Message]:
        model = session.query(MessageModel).filter(MessageModel.MessageID == message_id).first()
        return self._to_domain(model) if model else None
    
    def get_conversation(self, user1_id: int, user2_id: int, limit: int = 50, offset: int = 0) -> List[Message]:
        models = session.query(MessageModel).filter(
            ((MessageModel.SenderID == user1_id) & (MessageModel.ReceiverID == user2_id)) |
            ((MessageModel.SenderID == user2_id) & (MessageModel.ReceiverID == user1_id))
        ).order_by(MessageModel.SentAt.desc()).offset(offset).limit(limit).all()
        return [self._to_domain(model) for model in models]
    
    def get_user_conversations(self, user_id: int) -> List[dict]:
        # Get all unique conversations for a user
        conversations = session.query(MessageModel).filter(
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
            unread_count = session.query(MessageModel).filter(
                (MessageModel.SenderID == partner_id) & 
                (MessageModel.ReceiverID == user_id) & 
                (MessageModel.IsRead == False)
            ).count()
            conversation_dict[partner_id]['unread_count'] = unread_count
        
        return list(conversation_dict.values())
    
    def mark_as_read(self, sender_id: int, receiver_id: int) -> bool:
        messages = session.query(MessageModel).filter(
            (MessageModel.SenderID == sender_id) & 
            (MessageModel.ReceiverID == receiver_id) & 
            (MessageModel.IsRead == False)
        ).all()
        
        for message in messages:
            message.IsRead = True
            message.ReadAt = datetime.now()
        
        session.commit()
        return True
    
    def get_unread_count(self, user_id: int) -> int:
        return session.query(MessageModel).filter(
            (MessageModel.ReceiverID == user_id) & (MessageModel.IsRead == False)
        ).count()
    
    def delete(self, message_id: int) -> bool:
        model = session.query(MessageModel).filter(MessageModel.MessageID == message_id).first()
        if model:
            session.delete(model)
            session.commit()
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
