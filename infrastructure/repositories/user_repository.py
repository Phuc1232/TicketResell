from typing import List, Optional
from sqlalchemy.orm import Session
from infrastructure.databases.mssql import session
from infrastructure.models.user_model import UserModel
from domain.models.user import User
from domain.models.iuser_repository import IUserRepository


class UserRepository(IUserRepository):
    def __init__(self, session: Session = session):
        self.session = session

    # ORM -> Domain
    def _to_domain(self, model: UserModel) -> User:
        return User(
            id=model.UserId,
            phone_number=model.Phone_Number,
            username=model.UserName,
            status=model.Status,
            password_hash=model.Password,
            email=model.Email,
            date_of_birth=model.Date_Of_Birth,
            create_date=model.Create_Date,
            role_id=model.RoleID,
            verified=model.verified,
            verification_code=model.verification_code,
            verification_expires_at=model.verification_expires_at
        )

    # Domain -> ORM
    def _to_orm(self, user: User) -> UserModel:
        return UserModel(
            UserId=user.id,
            Phone_Number=user.phone_number,
            UserName=user.username,
            Status=user.status,
            Password=user.password_hash,
            Email=user.email,
            Date_Of_Birth=user.date_of_birth,
            Create_Date=user.create_date,
            RoleID=user.role_id,
            verified=user.verified,
            verification_code=user.verification_code,
            verification_expires_at=user.verification_expires_at
        )

    def add(self, user: User) -> User:
        try:
            model = self._to_orm(user)
            self.session.add(model)
            self.session.commit()
            self.session.refresh(model)
            return self._to_domain(model)
        except Exception:
            self.session.rollback()
            raise
        finally:
            self.session.close()

    def get_by_email(self, email: str) -> Optional[User]:
        model = self.session.query(UserModel).filter_by(Email=email).first()
        return self._to_domain(model) if model else None

    def get_by_id(self, user_id: int) -> Optional[User]:
        model = self.session.query(UserModel).filter_by(UserId=user_id).first()
        return self._to_domain(model) if model else None

    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        model = self.session.query(UserModel).filter_by(UserName=username).first()
        return self._to_domain(model) if model else None

    def list(self) -> List[User]:
        models = self.session.query(UserModel).all()
        return [self._to_domain(m) for m in models]

    def update(self, user: User) -> User:
        try:
            model = self.session.query(UserModel).filter_by(UserId=user.id).first()
            if not model:
                raise ValueError("User not found")

            model.Phone_Number = user.phone_number
            model.UserName = user.username
            model.Status = user.status
            model.Email = user.email
            model.Date_Of_Birth = user.date_of_birth
            model.RoleID = user.role_id
            # Update verification fields
            model.verified = user.verified
            model.verification_code = user.verification_code
            model.verification_expires_at = user.verification_expires_at

            self.session.commit()
            self.session.refresh(model)
            return self._to_domain(model)
        except Exception:
            self.session.rollback()
            raise
        finally:
            self.session.close()

    def get_by_role_id(self, role_id: int) -> List[User]:
        """Get all users with a specific role ID"""
        models = self.session.query(UserModel).filter_by(RoleID=role_id).all()
        return [self._to_domain(m) for m in models]

    def delete(self, user_id: int) -> None:
        import logging
        logger = logging.getLogger(__name__)

        try:
            model = self.session.query(UserModel).filter_by(UserId=user_id).first()
            if not model:
                logger.warning(f"User {user_id} not found for deletion")
                raise ValueError(f"User {user_id} not found")

            logger.info(f"Starting HARD DELETE for user {user_id}: {model.Email}")

            # Delete related data first to avoid foreign key constraints
            self._delete_user_related_data(user_id)
            logger.info(f"Deleted all related data for user {user_id}")

            # Then delete the user - FORCE DELETE
            self.session.delete(model)
            self.session.commit()
            logger.info(f"Successfully HARD DELETED user {user_id} from database")

        except Exception as e:
            logger.error(f"HARD DELETE FAILED for user {user_id}: {e}")
            self.session.rollback()
            raise Exception(f"Hard delete failed for user {user_id}: {e}")
        finally:
            self.session.close()

    def _delete_user_related_data(self, user_id: int) -> None:
        """
        Delete all data related to a user to avoid foreign key constraint violations

        Args:
            user_id: ID of the user whose related data should be deleted
        """
        import logging
        logger = logging.getLogger(__name__)

        try:
            # Import models here to avoid circular imports
            from infrastructure.models.Ticket_model import TicketModel
            from infrastructure.models.message_model import MessageModel
            from infrastructure.models.transaction_model import TransactionModel
            from infrastructure.models.support_model import SupportModel
            
            from infrastructure.models.feedback_model import UserFeedbackModel, TicketFeedbackModel

            # First, get all tickets owned by user to delete related messages
            user_tickets = self.session.query(TicketModel).filter_by(OwnerID=user_id).all()
            user_ticket_ids = [ticket.TicketID for ticket in user_tickets]

            # Delete messages related to user's tickets
            ticket_messages_deleted = 0
            if user_ticket_ids:
                ticket_messages_deleted = self.session.query(MessageModel).filter(
                    MessageModel.TicketID.in_(user_ticket_ids)
                ).delete(synchronize_session=False)

            # Delete messages sent or received by user (not related to tickets)
            user_messages_deleted = self.session.query(MessageModel).filter(
                (MessageModel.SenderID == user_id) |
                (MessageModel.ReceiverID == user_id)
            ).delete()

            total_messages_deleted = ticket_messages_deleted + user_messages_deleted
            logger.info(f"Deleted {total_messages_deleted} messages for user {user_id} (ticket-related: {ticket_messages_deleted}, user-related: {user_messages_deleted})")

            # Delete payments and transactions involving user (BEFORE deleting tickets)
            from infrastructure.models.payment_model import PaymentModel
            from infrastructure.models.earning_model import EarningModel

            # First get all transactions involving this user
            user_transactions = self.session.query(TransactionModel).filter(
                (TransactionModel.BuyerID == user_id) |
                (TransactionModel.SellerID == user_id)
            ).all()

            # Delete payments related to these transactions
            payments_deleted = 0
            earnings_deleted = 0
            for transaction in user_transactions:
                # Delete payments for this transaction
                payments_deleted += self.session.query(PaymentModel).filter_by(
                    TransactionID=transaction.TransactionID
                ).delete()

                # Delete earnings for this user (by date range around transaction)
                # Since earnings don't have TransactionID FK, we delete by UserID
                if transaction.SellerID == user_id:
                    earnings_deleted += self.session.query(EarningModel).filter_by(
                        UserID=user_id
                    ).delete()

            logger.info(f"Deleted {payments_deleted} payments and {earnings_deleted} earnings for user {user_id}")

            # Now delete transactions involving user
            transactions_deleted = self.session.query(TransactionModel).filter(
                (TransactionModel.BuyerID == user_id) |
                (TransactionModel.SellerID == user_id)
            ).delete()
            logger.info(f"Deleted {transactions_deleted} transactions for user {user_id}")

            # NOW delete tickets owned by user (after transactions are deleted)
            tickets_deleted = self.session.query(TicketModel).filter_by(OwnerID=user_id).delete()
            logger.info(f"Deleted {tickets_deleted} tickets for user {user_id}")

            
            

            # Delete user feedback given or received by user
            user_feedback_deleted = self.session.query(UserFeedbackModel).filter(
                (UserFeedbackModel.ReviewerID == user_id) |
                (UserFeedbackModel.TargetUserID == user_id)
            ).delete()

            # Delete ticket feedback given by user
            ticket_feedback_deleted = self.session.query(TicketFeedbackModel).filter_by(ReviewerID=user_id).delete()

            total_feedback_deleted = user_feedback_deleted + ticket_feedback_deleted
            logger.info(f"Deleted {total_feedback_deleted} feedback records for user {user_id} (user: {user_feedback_deleted}, ticket: {ticket_feedback_deleted})")
            
            # Delete support tickets created by user
            support_deleted = self.session.query(SupportModel).filter_by(UserID=user_id).delete()
            logger.info(f"Deleted {support_deleted} support tickets for user {user_id}")

            # Commit the related data deletion
            self.session.commit()
            logger.info(f"Successfully committed deletion of all related data for user {user_id}")

        except Exception as e:
            logger.error(f"Failed to delete related data for user {user_id}: {e}")
            self.session.rollback()
            raise Exception(f"Failed to delete user related data: {e}")
