from typing import List, Optional
from sqlalchemy.orm import Session
from infrastructure.databases.mssql import session
from infrastructure.models.Ticket_model import TicketModel
from domain.models.ticket import Ticket
from domain.models.itticket_repository import ITicketRepository


class TicketRepository(ITicketRepository):
    def __init__(self, session: Session = session):
        self.session = session

    # ORM -> Domain
    def _to_domain(self, model: TicketModel) -> Ticket:
        return Ticket(
            TicketID=model.TicketID,
            EventDate=model.EventDate,
            Price=model.Price,
            EventName=model.EventName,
            Status=model.Status,
            OwnerID=model.OwnerID
        )

    # Domain -> ORM
    def _to_orm(self, ticket: Ticket) -> TicketModel:
        return TicketModel(
            TicketID=ticket.TicketID,
            EventDate=ticket.EventDate,
            Price=ticket.Price,
            EventName=ticket.EventName,
            Status=ticket.Status,
            OwnerID=ticket.OwnerID
        )

    def add(self, ticket: Ticket) -> Ticket:
        try:
            model = self._to_orm(ticket)
            self.session.add(model)
            self.session.commit()
            self.session.refresh(model)
            return self._to_domain(model)
        except Exception:
            self.session.rollback()
            raise
        finally:
            self.session.close()

    def get_by_id(self, ticket_id: int) -> Optional[Ticket]:
        model = (
            self.session.query(TicketModel)
            .filter_by(TicketID=ticket_id)
            .first()
        )
        return self._to_domain(model) if model else None

    def list(self) -> List[Ticket]:
        models = self.session.query(TicketModel).all()
        return [self._to_domain(m) for m in models]

    def update(self, ticket: Ticket) -> Ticket:
        try:
            model = (
                self.session.query(TicketModel)
                .filter_by(TicketID=ticket.TicketID)
                .first()
            )
            if not model:
                raise ValueError("Ticket not found")

            model.EventDate = ticket.EventDate
            model.Price = ticket.Price
            model.EventName = ticket.EventName
            model.Status = ticket.Status
            model.OwnerID = ticket.OwnerID

            self.session.commit()
            self.session.refresh(model)
            return self._to_domain(model)
        except Exception:
            self.session.rollback()
            raise
        finally:
            self.session.close()

    def delete(self, ticket_id: int) -> None:
        try:
            model = (
                self.session.query(TicketModel)
                .filter_by(TicketID=ticket_id)
                .first()
            )
            if model:
                self.session.delete(model)
                self.session.commit()
        except Exception:
            self.session.rollback()
            raise
        finally:
            self.session.close()

    def search_tickets(self, **filters) -> List[Ticket]:
        """Search tickets with filters"""
        query = self.session.query(TicketModel)
        
        if filters.get('event_name'):
            query = query.filter(TicketModel.EventName.ilike(f"%{filters['event_name']}%"))
        
        if filters.get('min_price'):
            query = query.filter(TicketModel.Price >= filters['min_price'])
        
        if filters.get('max_price'):
            query = query.filter(TicketModel.Price <= filters['max_price'])
        
        if filters.get('date_from'):
            query = query.filter(TicketModel.EventDate >= filters['date_from'])
        
        if filters.get('date_to'):
            query = query.filter(TicketModel.EventDate <= filters['date_to'])
        
        if filters.get('status'):
            query = query.filter(TicketModel.Status == filters['status'])
        
        # Chỉ hiển thị tickets Available
        query = query.filter(TicketModel.Status == 'Available')
        
        # Sắp xếp theo giá tăng dần
        query = query.order_by(TicketModel.Price.asc())
        
        models = query.all()
        return [self._to_domain(m) for m in models]