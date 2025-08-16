from domain.models.ticket import Ticket
from domain.models.itticket_repository import ITicketRepository
from typing import List, Optional


class TicketService:
    def __init__(self, ticket_repository: ITicketRepository):
        self.ticket_repository = ticket_repository

    def list_tickets(self) -> List[Ticket]:
        return self.ticket_repository.list()

    def get_ticket(self, ticket_id: int) -> Optional[Ticket]:
        return self.ticket_repository.get_by_id(ticket_id)

    def create_ticket(self, EventDate, Price, EventName, Status, OwnerID) -> Ticket:
        ticket = Ticket(
            TicketID=None,
            EventDate=EventDate,
            Price=Price,
            EventName=EventName,
            Status=Status,
            OwnerID=OwnerID
        )
        return self.ticket_repository.add(ticket)

    def update_ticket(self, ticket_id: int, **kwargs) -> Optional[Ticket]:
        ticket = self.ticket_repository.get_by_id(ticket_id)
        if not ticket:
            return None
        for key, value in kwargs.items():
            setattr(ticket, key, value)
        return self.ticket_repository.update(ticket)

    def delete_ticket(self, ticket_id: int) -> bool:
        ticket = self.ticket_repository.get_by_id(ticket_id)
        if not ticket:
            return False
        self.ticket_repository.delete(ticket_id)
        return True
