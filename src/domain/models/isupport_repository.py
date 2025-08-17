from abc import ABC, abstractmethod
from typing import List, Optional
from domain.models.support import Support

class ISupportRepository(ABC):
    @abstractmethod
    def add(self, support: Support) -> Support:
        pass
    
    @abstractmethod
    def get_by_id(self, support_id: int) -> Optional[Support]:
        pass
    
    @abstractmethod
    def get_by_user_id(self, user_id: int) -> List[Support]:
        pass
    
    @abstractmethod
    def update(self, support: Support) -> Support:
        pass
    
    @abstractmethod
    def delete(self, support_id: int) -> bool:
        pass
    
    @abstractmethod
    def get_by_status(self, status: str) -> List[Support]:
        pass
    
    @abstractmethod
    def get_all(self) -> List[Support]:
        pass
    
    @abstractmethod
    def update_status(self, support_id: int, status: str) -> bool:
        pass
