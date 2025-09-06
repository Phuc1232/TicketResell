from domain.models.ticket import Ticket
from domain.models.itticket_repository import ITicketRepository
from typing import List, Optional
from datetime import datetime


class TicketService:
    def __init__(self, ticket_repository: ITicketRepository):
        self.ticket_repository = ticket_repository

    def list_tickets(self) -> List[Ticket]:
        return self.ticket_repository.list()

    def get_ticket(self, ticket_id: int) -> Optional[Ticket]:
        return self.ticket_repository.get_by_id(ticket_id)

    def get_ticket_by_event_and_owner(self, event_name: str, owner_username: str) -> Optional[Ticket]:
        """Get ticket by event name and owner username"""
        return self.ticket_repository.get_by_event_name_and_owner(event_name, owner_username)

    def create_ticket(self, EventDate, Price, EventName, Status, PaymentMethod, ContactInfo, OwnerID) -> Ticket:
        ticket = Ticket(
            TicketID=None,
            EventDate=EventDate,
            Price=Price,
            EventName=EventName,
            Status=Status,
            PaymentMethod=PaymentMethod,
            ContactInfo=ContactInfo,
            OwnerID=OwnerID
        )
        return self.ticket_repository.add(ticket)

    def update_ticket(self, ticket_id: int, **kwargs) -> Optional[Ticket]:
        ticket = self.ticket_repository.get_by_id(ticket_id)
        if not ticket:
            return None
        for key, value in kwargs.items():
            setattr(ticket, key, value)
        ticket.UpdatedAt = datetime.now()
        return self.ticket_repository.update(ticket)

    def delete_ticket(self, ticket_id: int) -> bool:
        ticket = self.ticket_repository.get_by_id(ticket_id)
        if not ticket:
            return False
        self.ticket_repository.delete(ticket_id)
        return True

    def search_tickets_by_event_name(self, event_name: str) -> List[Ticket]:
        """Search tickets by event name"""
        return self.ticket_repository.search_tickets_by_event_name(event_name)

    def search_tickets_advanced(self, event_name: str = None, event_type: str = None,
                               min_price: float = None, max_price: float = None,
                               location: str = None, ticket_type: str = None,
                               is_negotiable: bool = None, limit: int = 50) -> List[Ticket]:
        """Advanced search with multiple filters"""
        return self.ticket_repository.search_tickets_advanced(
            event_name, event_type, min_price, max_price, 
            location, ticket_type, is_negotiable, limit
        )

    def get_tickets_by_event_type(self, event_type: str, limit: int = 20) -> List[Ticket]:
        """Get tickets by event type"""
        return self.ticket_repository.get_tickets_by_event_type(event_type, limit)

    def get_trending_tickets(self, limit: int = 10) -> List[Ticket]:
        """Get trending tickets"""
        return self.ticket_repository.get_trending_tickets(limit)

    def increment_view_count(self, ticket_id: int) -> None:
        """Increment view count for a ticket"""
        self.ticket_repository.increment_view_count(ticket_id)

    def update_rating(self, ticket_id: int, new_rating: float) -> None:
        """Update ticket rating"""
        if 0 <= new_rating <= 5:  # Validate rating range
            self.ticket_repository.update_rating(ticket_id, new_rating)
        else:
            raise ValueError("Rating must be between 0 and 5")

    def get_tickets_by_owner(self, owner_id: int) -> List[Ticket]:
        """Get tickets by owner ID"""
        return self.ticket_repository.get_tickets_by_owner(owner_id)
