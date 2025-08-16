from abc import ABC, abstractmethod
from typing import List, Optional
from .ticket import Ticket

class ITicketRepository(ABC):
    @abstractmethod
    def add(self, ticket: Ticket) -> Ticket:
        pass

    @abstractmethod
    def get_by_id(self, ticket_id: int) -> Optional[Ticket]:
        pass

    @abstractmethod
    def list(self) -> List[Ticket]:
        pass


    @abstractmethod
    def update(self, ticket: Ticket) -> Ticket:
        pass

    @abstractmethod
    def delete(self, ticket_id: int) -> None:
        pass
