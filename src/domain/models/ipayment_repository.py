from abc import ABC, abstractmethod
from typing import List, Optional
from domain.models.payment import Payment

class IPaymentRepository(ABC):
    @abstractmethod
    def add(self, payment: Payment) -> Payment:
        pass
    
    @abstractmethod
    def get_by_id(self, payment_id: int) -> Optional[Payment]:
        pass
    
    @abstractmethod
    def get_by_user_id(self, user_id: int) -> List[Payment]:
        pass
    
    @abstractmethod
    def get_by_transaction_id(self, transaction_id: int) -> Optional[Payment]:
        pass
    
    @abstractmethod
    def update(self, payment: Payment) -> Payment:
        pass
    
    @abstractmethod
    def delete(self, payment_id: int) -> bool:
        pass
    
    @abstractmethod
    def get_by_status(self, status: str) -> List[Payment]:
        pass

    @abstractmethod
    def get_user_payments_paginated(self, user_id: int, limit: int, offset: int) -> List[Payment]:
        pass

    @abstractmethod
    def get_user_payments_count(self, user_id: int) -> int:
        pass
