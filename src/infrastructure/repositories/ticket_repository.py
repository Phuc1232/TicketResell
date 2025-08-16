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
            PaymentMethod=model.PaymentMethod,
            ContactInfo=model.ContactInfo,
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
            PaymentMethod=ticket.PaymentMethod,
            ContactInfo=ticket.ContactInfo,
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
            model.PaymentMethod = ticket.PaymentMethod
            model.ContactInfo = ticket.ContactInfo
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

    def get_tickets_by_owner(self, owner_id: int) -> List[Ticket]:
        """Get tickets by owner ID"""
        models = (
            self.session.query(TicketModel)
            .filter_by(OwnerID=owner_id)
            .order_by(TicketModel.EventDate.desc())
            .all()
        )
        return [self._to_domain(m) for m in models]

    def search_tickets_by_event_name(self, event_name: str, limit: int = 50) -> List[Ticket]:
        """Search tickets by event name only with pagination"""
        query = self.session.query(TicketModel)
        
        # Tìm kiếm theo tên sự kiện (không phân biệt hoa thường)
        query = query.filter(TicketModel.EventName.ilike(f"%{event_name}%"))
        
        # Chỉ hiển thị tickets Available
        query = query.filter(TicketModel.Status == 'Available')
        
        # Sắp xếp theo giá tăng dần
        query = query.order_by(TicketModel.Price.asc())
        
        # Giới hạn số lượng kết quả
        query = query.limit(limit)
        
        models = query.all()
        return [self._to_domain(m) for m in models]

    def search_tickets_advanced(self, event_name: str = None, event_type: str = None, 
                               min_price: float = None, max_price: float = None,
                               location: str = None, ticket_type: str = None,
                               is_negotiable: bool = None, limit: int = 50) -> List[Ticket]:
        """Advanced search with multiple filters"""
        query = self.session.query(TicketModel)
        
        if event_name:
            query = query.filter(TicketModel.EventName.ilike(f"%{event_name}%"))
        
        if event_type:
            query = query.filter(TicketModel.EventType == event_type)
        
        if min_price is not None:
            query = query.filter(TicketModel.Price >= min_price)
        
        if max_price is not None:
            query = query.filter(TicketModel.Price <= max_price)
        
        if location:
            query = query.filter(TicketModel.EventLocation.ilike(f"%{location}%"))
        
        if ticket_type:
            query = query.filter(TicketModel.TicketType == ticket_type)
        
        if is_negotiable is not None:
            query = query.filter(TicketModel.IsNegotiable == is_negotiable)
        
        # Chỉ hiển thị tickets Available
        query = query.filter(TicketModel.Status == 'Available')
        
        # Sắp xếp theo rating giảm dần, sau đó theo giá tăng dần
        query = query.order_by(TicketModel.Rating.desc().nullslast(), TicketModel.Price.asc())
        
        # Giới hạn số lượng kết quả
        query = query.limit(limit)
        
        models = query.all()
        return [self._to_domain(m) for m in models]

    def get_tickets_by_event_type(self, event_type: str, limit: int = 20) -> List[Ticket]:
        """Get tickets by event type"""
        models = (
            self.session.query(TicketModel)
            .filter_by(EventType=event_type, Status='Available')
            .order_by(TicketModel.EventDate.asc())
            .limit(limit)
            .all()
        )
        return [self._to_domain(m) for m in models]

    def get_trending_tickets(self, limit: int = 10) -> List[Ticket]:
        """Get trending tickets based on view count and rating"""
        models = (
            self.session.query(TicketModel)
            .filter_by(Status='Available')
            .order_by(TicketModel.ViewCount.desc(), TicketModel.Rating.desc().nullslast())
            .limit(limit)
            .all()
        )
        return [self._to_domain(m) for m in models]

    def increment_view_count(self, ticket_id: int) -> None:
        """Increment view count for a ticket"""
        try:
            model = (
                self.session.query(TicketModel)
                .filter_by(TicketID=ticket_id)
                .first()
            )
            if model:
                model.ViewCount += 1
                self.session.commit()
        except Exception:
            self.session.rollback()
            raise
        finally:
            self.session.close()

    def update_rating(self, ticket_id: int, new_rating: float) -> None:
        """Update ticket rating"""
        try:
            model = (
                self.session.query(TicketModel)
                .filter_by(TicketID=ticket_id)
                .first()
            )
            if model:
                # Tính rating trung bình
                if model.Rating is None:
                    model.Rating = new_rating
                    model.ReviewCount = 1
                else:
                    total_rating = model.Rating * model.ReviewCount + new_rating
                    model.ReviewCount += 1
                    model.Rating = total_rating / model.ReviewCount
                
                self.session.commit()
        except Exception:
            self.session.rollback()
            raise
        finally:
            self.session.close()