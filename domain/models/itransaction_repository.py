from abc import ABC, abstractmethod
from typing import List, Optional
from domain.models.transaction import Transaction

class ITransactionRepository(ABC):
    @abstractmethod
    def add(self, transaction: Transaction) -> Transaction:
        pass
    
    @abstractmethod
    def get_by_id(self, transaction_id: int) -> Optional[Transaction]:
        pass
    
    @abstractmethod
    def get_by_ticket_id(self, ticket_id: int) -> List[Transaction]:
        pass
    
    @abstractmethod
    def get_by_user_id(self, user_id: int) -> List[Transaction]:
        pass
    
    @abstractmethod
    def update(self, transaction: Transaction) -> Transaction:
        pass
    
    @abstractmethod
    def delete(self, transaction_id: int) -> bool:
        pass
    
    @abstractmethod
    def list(self) -> List[Transaction]:
        pass
