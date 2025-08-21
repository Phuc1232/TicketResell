from typing import List, Optional, Dict, Any
from domain.models.feedback import Feedback, TicketFeedback
from domain.models.ifeedback_repository import IFeedbackRepository
from domain.models.iuser_repository import IUserRepository
from domain.models.itticket_repository import ITicketRepository
from domain.models.itransaction_repository import ITransactionRepository
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class FeedbackService:
    def __init__(self, feedback_repository: IFeedbackRepository, user_repository: IUserRepository,
                 ticket_repository: ITicketRepository, transaction_repository: ITransactionRepository):
        self.feedback_repository = feedback_repository
        self.user_repository = user_repository
        self.ticket_repository = ticket_repository
        self.transaction_repository = transaction_repository
    
    def submit_user_feedback(self, reviewer_id: int, target_user_id: int, rating: float,
                           comment: Optional[str] = None, transaction_id: Optional[int] = None) -> Feedback:
        # Validate reviewer exists
        reviewer = self.user_repository.get_by_id(reviewer_id)
        if not reviewer:
            raise ValueError("Reviewer not found")

        # Validate target user exists
        target_user = self.user_repository.get_by_id(target_user_id)
        if not target_user:
            raise ValueError("Target user not found")

        # Prevent self-feedback
        if reviewer_id == target_user_id:
            raise ValueError("Cannot provide feedback for yourself")

        # Validate rating range
        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5")

        # Validate transaction exists if provided and involves both users
        if transaction_id:
            transaction = self.transaction_repository.get_by_id(transaction_id)
            if not transaction:
                raise ValueError("Transaction not found")

            # Check if both users are involved in the transaction
            if not ((transaction.BuyerID == reviewer_id and transaction.SellerID == target_user_id) or
                   (transaction.SellerID == reviewer_id and transaction.BuyerID == target_user_id)):
                raise ValueError("You can only provide feedback for users you've transacted with")

            # Check if feedback already exists for this transaction
            existing_feedback = self.feedback_repository.get_feedback_by_transaction(transaction_id, reviewer_id)
            if existing_feedback:
                raise ValueError("Feedback already provided for this transaction")

        # Create feedback
        feedback = Feedback(
            FeedbackID=None,
            ReviewerID=reviewer_id,
            TargetUserID=target_user_id,
            Rating=rating,
            Comment=comment,
            TransactionID=transaction_id,
            CreatedAt=datetime.now()
        )

        created_feedback = self.feedback_repository.add_user_feedback(feedback)

        logger.info(f"User feedback submitted: reviewer={reviewer_id}, target={target_user_id}, rating={rating}")

        return created_feedback
    
    def submit_ticket_feedback(self, reviewer_id: int, ticket_id: int, rating: float, 
                             comment: Optional[str] = None) -> TicketFeedback:
        # Validate reviewer exists
        reviewer = self.user_repository.get_by_id(reviewer_id)
        if not reviewer:
            raise ValueError("Reviewer not found")
        
        # Validate ticket exists
        ticket = self.ticket_repository.get_by_id(ticket_id)
        if not ticket:
            raise ValueError("Ticket not found")
        
        # Validate rating range
        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5")
        
        # Create ticket feedback
        feedback = TicketFeedback(
            FeedbackID=None,
            ReviewerID=reviewer_id,
            TicketID=ticket_id,
            Rating=rating,
            Comment=comment,
            CreatedAt=datetime.now()
        )
        
        return self.feedback_repository.add_ticket_feedback(feedback)
    
    def get_user_feedback(self, user_id: int, limit: int = 20, offset: int = 0) -> List[Feedback]:
        # Validate user exists
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        return self.feedback_repository.get_user_feedback(user_id, limit, offset)
    
    def get_ticket_feedback(self, ticket_id: int, limit: int = 20, offset: int = 0) -> List[TicketFeedback]:
        # Validate ticket exists
        ticket = self.ticket_repository.get_by_id(ticket_id)
        if not ticket:
            raise ValueError("Ticket not found")
        
        return self.feedback_repository.get_ticket_feedback(ticket_id, limit, offset)
    
    def get_average_user_rating(self, user_id: int) -> float:
        # Validate user exists
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        return self.feedback_repository.get_average_user_rating(user_id)
    
    def get_average_ticket_rating(self, ticket_id: int) -> float:
        # Validate ticket exists
        ticket = self.ticket_repository.get_by_id(ticket_id)
        if not ticket:
            raise ValueError("Ticket not found")
        
        return self.feedback_repository.get_average_ticket_rating(ticket_id)
    
    def delete_user_feedback(self, feedback_id: int, user_id: int) -> bool:
        # Validate user exists
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Check if user owns the feedback
        feedback_list = self.feedback_repository.get_user_feedback(user_id, limit=1000, offset=0)
        feedback = next((f for f in feedback_list if f.FeedbackID == feedback_id), None)
        if not feedback or feedback.ReviewerID != user_id:
            raise ValueError("Feedback not found or access denied")
        
        return self.feedback_repository.delete_user_feedback(feedback_id)
    
    def delete_ticket_feedback(self, feedback_id: int, user_id: int) -> bool:
        # Validate user exists
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Check if user owns the feedback
        feedback_list = self.feedback_repository.get_ticket_feedback(0, limit=1000, offset=0)  # This needs to be improved
        feedback = next((f for f in feedback_list if f.FeedbackID == feedback_id), None)
        if not feedback or feedback.ReviewerID != user_id:
            raise ValueError("Feedback not found or access denied")
        
        return self.feedback_repository.delete_ticket_feedback(feedback_id)

    def get_user_feedback_summary(self, user_id: int) -> Dict[str, Any]:
        """
        Get comprehensive feedback summary for a user

        Args:
            user_id: User ID to get feedback summary for

        Returns:
            Dict with feedback statistics and recent feedback
        """
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        # Get all feedback for user
        all_feedback = self.feedback_repository.get_user_feedback(user_id, limit=1000, offset=0)

        if not all_feedback:
            return {
                'user_id': user_id,
                'average_rating': 0.0,
                'total_feedback': 0,
                'rating_distribution': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
                'recent_feedback': [],
                'feedback_trend': 'neutral'
            }

        # Calculate statistics
        total_feedback = len(all_feedback)
        average_rating = sum(f.Rating for f in all_feedback) / total_feedback

        # Rating distribution
        rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for feedback in all_feedback:
            rating_distribution[int(feedback.Rating)] += 1

        # Recent feedback (last 5)
        recent_feedback = sorted(all_feedback, key=lambda x: x.CreatedAt, reverse=True)[:5]
        recent_feedback_data = []
        for feedback in recent_feedback:
            reviewer = self.user_repository.get_by_id(feedback.ReviewerID)
            recent_feedback_data.append({
                'feedback_id': feedback.FeedbackID,
                'reviewer_name': reviewer.username if reviewer else 'Unknown',
                'rating': feedback.Rating,
                'comment': feedback.Comment,
                'created_at': feedback.CreatedAt.isoformat(),
                'transaction_id': feedback.TransactionID
            })

        # Calculate trend (last 30 days vs previous 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        sixty_days_ago = datetime.now() - timedelta(days=60)

        recent_ratings = [f.Rating for f in all_feedback if f.CreatedAt >= thirty_days_ago]
        previous_ratings = [f.Rating for f in all_feedback if sixty_days_ago <= f.CreatedAt < thirty_days_ago]

        trend = 'neutral'
        if recent_ratings and previous_ratings:
            recent_avg = sum(recent_ratings) / len(recent_ratings)
            previous_avg = sum(previous_ratings) / len(previous_ratings)
            if recent_avg > previous_avg + 0.2:
                trend = 'improving'
            elif recent_avg < previous_avg - 0.2:
                trend = 'declining'

        return {
            'user_id': user_id,
            'average_rating': round(average_rating, 2),
            'total_feedback': total_feedback,
            'rating_distribution': rating_distribution,
            'recent_feedback': recent_feedback_data,
            'feedback_trend': trend,
            'recent_feedback_count': len(recent_ratings),
            'previous_feedback_count': len(previous_ratings)
        }

    def get_feedback_analytics(self, user_id: int) -> Dict[str, Any]:
        """
        Get detailed feedback analytics for a user

        Args:
            user_id: User ID to get analytics for

        Returns:
            Dict with detailed analytics
        """
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        # Get feedback as buyer and seller
        buyer_feedback = self.feedback_repository.get_feedback_as_buyer(user_id)
        seller_feedback = self.feedback_repository.get_feedback_as_seller(user_id)

        # Calculate buyer statistics
        buyer_stats = self._calculate_feedback_stats(buyer_feedback, 'buyer')

        # Calculate seller statistics
        seller_stats = self._calculate_feedback_stats(seller_feedback, 'seller')

        return {
            'user_id': user_id,
            'buyer_analytics': buyer_stats,
            'seller_analytics': seller_stats,
            'overall_reputation_score': self._calculate_reputation_score(buyer_feedback + seller_feedback)
        }

    def _calculate_feedback_stats(self, feedback_list: List[Feedback], role: str) -> Dict[str, Any]:
        """Calculate statistics for a list of feedback"""
        if not feedback_list:
            return {
                'average_rating': 0.0,
                'total_feedback': 0,
                'rating_distribution': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
                'role': role
            }

        total = len(feedback_list)
        average = sum(f.Rating for f in feedback_list) / total

        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for feedback in feedback_list:
            distribution[int(feedback.Rating)] += 1

        return {
            'average_rating': round(average, 2),
            'total_feedback': total,
            'rating_distribution': distribution,
            'role': role
        }

    def _calculate_reputation_score(self, all_feedback: List[Feedback]) -> float:
        """
        Calculate overall reputation score based on feedback

        Args:
            all_feedback: List of all feedback for user

        Returns:
            Reputation score (0-100)
        """
        if not all_feedback:
            return 0.0

        # Base score from average rating
        average_rating = sum(f.Rating for f in all_feedback) / len(all_feedback)
        base_score = (average_rating / 5.0) * 70  # 70% weight for rating

        # Bonus for volume (up to 20 points)
        volume_bonus = min(len(all_feedback) * 0.5, 20)

        # Recency bonus (up to 10 points)
        recent_feedback = [f for f in all_feedback if f.CreatedAt >= datetime.now() - timedelta(days=90)]
        recency_bonus = min(len(recent_feedback) * 0.2, 10)

        total_score = base_score + volume_bonus + recency_bonus
        return min(round(total_score, 1), 100.0)
