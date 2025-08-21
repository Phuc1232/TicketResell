from typing import List, Optional
from domain.models.feedback import Feedback, TicketFeedback
from domain.models.ifeedback_repository import IFeedbackRepository
from infrastructure.models.feedback_model import UserFeedbackModel, TicketFeedbackModel
from sqlalchemy import func

class FeedbackRepository(IFeedbackRepository):
    def __init__(self, session=None):
        if session is None:
            from infrastructure.databases.mssql import session as default_session
            self.session = default_session
        else:
            self.session = session
    def add_user_feedback(self, feedback: Feedback) -> Feedback:
        model = UserFeedbackModel(
            ReviewerID=feedback.ReviewerID,
            TargetUserID=feedback.TargetUserID,
            Rating=feedback.Rating,
            Comment=feedback.Comment,
            TransactionID=feedback.TransactionID,
            CreatedAt=feedback.CreatedAt
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_domain_user_feedback(model)
    
    def add_ticket_feedback(self, feedback: TicketFeedback) -> TicketFeedback:
        model = TicketFeedbackModel(
            ReviewerID=feedback.ReviewerID,
            TicketID=feedback.TicketID,
            Rating=feedback.Rating,
            Comment=feedback.Comment,
            CreatedAt=feedback.CreatedAt
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_domain_ticket_feedback(model)
    
    def get_user_feedback(self, user_id: int, limit: int = 20, offset: int = 0) -> List[Feedback]:
        models = self.session.query(UserFeedbackModel).filter(
            UserFeedbackModel.TargetUserID == user_id
        ).order_by(UserFeedbackModel.CreatedAt.desc()).offset(offset).limit(limit).all()
        return [self._to_domain_user_feedback(model) for model in models]
    
    def get_ticket_feedback(self, ticket_id: int, limit: int = 20, offset: int = 0) -> List[TicketFeedback]:
        models = self.session.query(TicketFeedbackModel).filter(
            TicketFeedbackModel.TicketID == ticket_id
        ).order_by(TicketFeedbackModel.CreatedAt.desc()).offset(offset).limit(limit).all()
        return [self._to_domain_ticket_feedback(model) for model in models]
    
    def get_average_user_rating(self, user_id: int) -> float:
        result = self.session.query(func.avg(UserFeedbackModel.Rating)).filter(
            UserFeedbackModel.TargetUserID == user_id
        ).scalar()
        return float(result) if result else 0.0
    
    def get_average_ticket_rating(self, ticket_id: int) -> float:
        result = self.session.query(func.avg(TicketFeedbackModel.Rating)).filter(
            TicketFeedbackModel.TicketID == ticket_id
        ).scalar()
        return float(result) if result else 0.0
    
    def delete_user_feedback(self, feedback_id: int) -> bool:
        model = self.session.query(UserFeedbackModel).filter(UserFeedbackModel.FeedbackID == feedback_id).first()
        if model:
            self.session.delete(model)
            self.session.commit()
            return True
        return False
    
    def delete_ticket_feedback(self, feedback_id: int) -> bool:
        model = self.session.query(TicketFeedbackModel).filter(TicketFeedbackModel.FeedbackID == feedback_id).first()
        if model:
            self.session.delete(model)
            self.session.commit()
            return True
        return False

    def get_feedback_by_transaction(self, transaction_id: int, reviewer_id: int) -> Optional[Feedback]:
        model = self.session.query(UserFeedbackModel).filter(
            UserFeedbackModel.TransactionID == transaction_id,
            UserFeedbackModel.ReviewerID == reviewer_id
        ).first()
        return self._to_domain_user_feedback(model) if model else None

    def get_feedback_as_buyer(self, user_id: int) -> List[Feedback]:
        # Get feedback where user was the buyer (feedback given to sellers)
        from infrastructure.models.transaction_model import TransactionModel
        models = self.session.query(UserFeedbackModel).join(
            TransactionModel, UserFeedbackModel.TransactionID == TransactionModel.TransactionID
        ).filter(
            TransactionModel.BuyerID == user_id,
            UserFeedbackModel.ReviewerID == user_id
        ).all()
        return [self._to_domain_user_feedback(model) for model in models]

    def get_feedback_as_seller(self, user_id: int) -> List[Feedback]:
        # Get feedback where user was the seller (feedback given to buyers)
        from infrastructure.models.transaction_model import TransactionModel
        models = self.session.query(UserFeedbackModel).join(
            TransactionModel, UserFeedbackModel.TransactionID == TransactionModel.TransactionID
        ).filter(
            TransactionModel.SellerID == user_id,
            UserFeedbackModel.ReviewerID == user_id
        ).all()
        return [self._to_domain_user_feedback(model) for model in models]

    def _to_domain_user_feedback(self, model: UserFeedbackModel) -> Feedback:
        return Feedback(
            FeedbackID=model.FeedbackID,
            ReviewerID=model.ReviewerID,
            TargetUserID=model.TargetUserID,
            Rating=model.Rating,
            Comment=model.Comment,
            TransactionID=model.TransactionID,
            CreatedAt=model.CreatedAt
        )
    
    def _to_domain_ticket_feedback(self, model: TicketFeedbackModel) -> TicketFeedback:
        return TicketFeedback(
            FeedbackID=model.FeedbackID,
            ReviewerID=model.ReviewerID,
            TicketID=model.TicketID,
            Rating=model.Rating,
            Comment=model.Comment,
            CreatedAt=model.CreatedAt
        )
