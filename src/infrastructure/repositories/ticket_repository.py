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

    def get_by_event_name_and_owner(self, event_name: str, owner_username: str) -> Optional[Ticket]:
        """Get ticket by event name and owner username"""
        from infrastructure.models.user_model import UserModel

        # Join với user table để lấy ticket theo event_name và owner username
        result = self.session.query(TicketModel).join(
            UserModel, TicketModel.OwnerID == UserModel.UserId
        ).filter(
            TicketModel.EventName == event_name,
            UserModel.UserName == owner_username
        ).first()

        return self._to_domain(result) if result else None

    def list(self) -> List[Ticket]:
        models = self.session.query(TicketModel).all()
        return [self._to_domain(m) for m in models]

    def update(self, ticket: Ticket) -> Ticket:
        try:
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Updating ticket {ticket.TicketID} with status {ticket.Status}")
            
            model = (
                self.session.query(TicketModel)
                .filter_by(TicketID=ticket.TicketID)
                .first()
            )
            if not model:
                logger.error(f"Ticket not found with ID: {ticket.TicketID}")
                raise ValueError("Ticket not found")

            logger.info(f"Current ticket status: {model.Status}, updating to: {ticket.Status}")
            
            model.EventDate = ticket.EventDate
            model.Price = ticket.Price
            model.EventName = ticket.EventName
            model.Status = ticket.Status
            model.PaymentMethod = ticket.PaymentMethod
            model.ContactInfo = ticket.ContactInfo
            model.OwnerID = ticket.OwnerID

            self.session.commit()
            self.session.refresh(model)
            logger.info(f"Ticket {ticket.TicketID} updated successfully, new status: {model.Status}")
            return self._to_domain(model)
        except Exception as e:
            self.session.rollback()
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error updating ticket {ticket.TicketID}: {str(e)}")
            raise
        finally:
            self.session.close()

    def delete(self, ticket_id: int) -> None:
        """Hard delete ticket and all related data"""
        import logging
        logger = logging.getLogger(__name__)

        try:
            model = (
                self.session.query(TicketModel)
                .filter_by(TicketID=ticket_id)
                .first()
            )
            if not model:
                logger.warning(f"Ticket {ticket_id} not found for deletion")
                raise ValueError(f"Ticket {ticket_id} not found")

            logger.info(f"Starting HARD DELETE for ticket {ticket_id}: {model.EventName}")

            # Delete related data first to avoid foreign key constraints
            self._delete_ticket_related_data(ticket_id)
            logger.info(f"Deleted all related data for ticket {ticket_id}")

            # Then delete the ticket - FORCE DELETE
            self.session.delete(model)
            self.session.commit()
            logger.info(f"Successfully HARD DELETED ticket {ticket_id} from database")

        except Exception:
            self.session.rollback()
            raise
        finally:
            self.session.close()

    def _delete_ticket_related_data(self, ticket_id: int):
        """Delete all data related to a ticket"""
        import logging
        logger = logging.getLogger(__name__)

        try:
            # Import models here to avoid circular imports
            from infrastructure.models.transaction_model import TransactionModel
            from infrastructure.models.feedback_model import UserFeedbackModel, TicketFeedbackModel
            from infrastructure.models.payment_model import PaymentModel
            from infrastructure.models.earning_model import EarningModel
            
            import datetime

            # 1. Delete transactions related to this ticket
            transactions = self.session.query(TransactionModel).filter_by(TicketID=ticket_id).all()
            for transaction in transactions:
                logger.info(f"Deleting transaction {transaction.TransactionID} for ticket {ticket_id}")

                # Delete payments related to this transaction
                payments = self.session.query(PaymentModel).filter_by(TransactionID=transaction.TransactionID).all()
                for payment in payments:
                    logger.info(f"Deleting payment {payment.PaymentID}")
                    self.session.delete(payment)

                # Note: Earnings are not directly linked to transactions via foreign key
                # They are linked by UserID only, so we skip deleting earnings
                # to avoid accidentally deleting unrelated earnings
                logger.info(f"Skipping earnings deletion for transaction {transaction.TransactionID} - no direct FK relationship")

                # Delete feedbacks related to this transaction
                user_feedbacks = self.session.query(UserFeedbackModel).filter_by(TransactionID=transaction.TransactionID).all()
                for feedback in user_feedbacks:
                    logger.info(f"Deleting user feedback {feedback.FeedbackID}")
                    self.session.delete(feedback)

                # Delete the transaction itself
                self.session.delete(transaction)

            # 2. Delete ticket feedbacks (if any)
            ticket_feedbacks = self.session.query(TicketFeedbackModel).filter_by(TicketID=ticket_id).all()
            for feedback in ticket_feedbacks:
                logger.info(f"Deleting ticket feedback {feedback.FeedbackID}")
                self.session.delete(feedback)

            

            # Commit all deletions
            self.session.commit()
            logger.info(f"Successfully deleted all related data for ticket {ticket_id}")

        except Exception as e:
            logger.error(f"Error deleting related data for ticket {ticket_id}: {str(e)}")
            self.session.rollback()
            raise

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