from abc import ABC, abstractmethod
from typing import List, Optional
from domain.models.message import Message

class IMessageRepository(ABC):
    @abstractmethod
    def add(self, message: Message) -> Message:
        pass
    
    @abstractmethod
    def get_by_id(self, message_id: int) -> Optional[Message]:
        pass
    
    @abstractmethod
    def get_conversation(self, user1_id: int, user2_id: int, limit: int = 50, offset: int = 0) -> List[Message]:
        pass
    
    @abstractmethod
    def get_user_conversations(self, user_id: int) -> List[dict]:
        pass
    
    @abstractmethod
    def mark_as_read(self, sender_id: int, receiver_id: int) -> bool:
        pass
    
    @abstractmethod
    def get_unread_count(self, user_id: int) -> int:
        pass
    
    @abstractmethod
    def delete(self, message_id: int) -> bool:
        pass

    @abstractmethod
    def search_messages(self, user_id: int, query: str, other_user_id: Optional[int] = None, limit: int = 20, offset: int = 0) -> List[Message]:
        pass

    @abstractmethod
    def get_user_stats(self, user_id: int) -> dict:
        pass
