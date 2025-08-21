from abc import ABC, abstractmethod
from typing import List, Optional
from domain.models.notification import Notification
from datetime import datetime

class INotificationRepository(ABC):
    @abstractmethod
    def add(self, notification: Notification) -> Notification:
        pass
    
    @abstractmethod
    def get_by_id(self, notification_id: int) -> Optional[Notification]:
        pass
    
    @abstractmethod
    def get_by_user_id(self, user_id: int, limit: int = 20, offset: int = 0, unread_only: bool = False) -> List[Notification]:
        pass
    
    @abstractmethod
    def mark_as_read(self, notification_id: int) -> bool:
        pass
    
    @abstractmethod
    def mark_all_as_read(self, user_id: int) -> bool:
        pass
    
    @abstractmethod
    def get_unread_count(self, user_id: int) -> int:
        pass
    
    @abstractmethod
    def delete(self, notification_id: int) -> bool:
        pass

    @abstractmethod
    def delete_older_than(self, cutoff_date: datetime) -> int:
        pass

    @abstractmethod
    def get_by_type(self, user_id: int, notification_type: str, limit: int = 20, offset: int = 0) -> List[Notification]:
        pass
