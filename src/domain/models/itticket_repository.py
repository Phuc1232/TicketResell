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
    def get_by_event_name_and_owner(self, event_name: str, owner_username: str) -> Optional[Ticket]:
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

    @abstractmethod
    def search_tickets_by_event_name(self, event_name: str) -> List[Ticket]:
        pass

    @abstractmethod
    def search_tickets_advanced(self, event_name: str = None, event_type: str = None, 
                               min_price: float = None, max_price: float = None,
                               location: str = None, ticket_type: str = None,
                               is_negotiable: bool = None, limit: int = 50) -> List[Ticket]:
        pass

    @abstractmethod
    def get_tickets_by_event_type(self, event_type: str, limit: int = 20) -> List[Ticket]:
        pass

    @abstractmethod
    def get_trending_tickets(self, limit: int = 10) -> List[Ticket]:
        pass

    @abstractmethod
    def increment_view_count(self, ticket_id: int) -> None:
        pass

    @abstractmethod
    def update_rating(self, ticket_id: int, new_rating: float) -> None:
        pass
