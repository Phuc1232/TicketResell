from abc import ABC, abstractmethod
from typing import List, Optional
from domain.models.earning import Earning

class IEarningRepository(ABC):
    @abstractmethod
    def add(self, earning: Earning) -> Earning:
        pass
    
    @abstractmethod
    def get_by_id(self, earning_id: int) -> Optional[Earning]:
        pass
    
    @abstractmethod
    def get_by_user_id(self, user_id: int) -> List[Earning]:
        pass
    
    @abstractmethod
    def update(self, earning: Earning) -> Earning:
        pass
    
    @abstractmethod
    def delete(self, earning_id: int) -> bool:
        pass
    
    @abstractmethod
    def get_total_earnings_by_user(self, user_id: int) -> float:
        pass
    
    @abstractmethod
    def get_earnings_by_date_range(self, user_id: int, start_date, end_date) -> List[Earning]:
        pass
