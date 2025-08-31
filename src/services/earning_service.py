from typing import List, Optional, Dict, Any
from domain.models.earning import Earning
from domain.models.iearning_repository import IEarningRepository
from domain.models.iuser_repository import IUserRepository
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class EarningService:
    def __init__(self, earning_repository: IEarningRepository, user_repository: IUserRepository):
        self.earning_repository = earning_repository
        self.user_repository = user_repository
    
    def create_earning(self, user_id: int, total_amount: float) -> Earning:
        # Validate user exists
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Create earning record
        earning = Earning(
            EarningID=None,
            UserID=user_id,
            TotalAmount=total_amount,
            Date=datetime.now()
        )
        
        return self.earning_repository.add(earning)
    
    def get_earning(self, earning_id: int) -> Optional[Earning]:
        return self.earning_repository.get_by_id(earning_id)
    
    def get_user_earnings(self, user_id: int) -> List[Earning]:
        # Validate user exists
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        return self.earning_repository.get_by_user_id(user_id)
    
    def get_total_user_earnings(self, user_id: int) -> float:
        # Validate user exists
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        return self.earning_repository.get_total_earnings_by_user(user_id)
    
    def get_earnings_by_date_range(self, user_id: int, start_date, end_date) -> List[Earning]:
        # Validate user exists
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        return self.earning_repository.get_earnings_by_date_range(user_id, start_date, end_date)
    
    def update_earning(self, earning_id: int, total_amount: float) -> Optional[Earning]:
        earning = self.earning_repository.get_by_id(earning_id)
        if not earning:
            return None
        
        earning.TotalAmount = total_amount
        earning.Date = datetime.now()
        
        return self.earning_repository.update(earning)
    
    def delete_earning(self, earning_id: int) -> bool:
        earning = self.earning_repository.get_by_id(earning_id)
        if not earning:
            return False
        
        return self.earning_repository.delete(earning_id)
    
    def add_earning_from_transaction(self, user_id: int, transaction_amount: float, commission_rate: float = 0.05) -> Earning:
        """Add earning from a successful transaction with commission"""
        earning_amount = transaction_amount * commission_rate
        return self.create_earning(user_id, earning_amount)

    def calculate_seller_earnings(self, user_id: int, transaction_amount: float, platform_commission: float = 0.05) -> Dict[str, float]:
        """
        Calculate seller earnings after platform commission

        Args:
            user_id: Seller user ID
            transaction_amount: Total transaction amount
            platform_commission: Platform commission rate (default 5%)

        Returns:
            Dict with earnings breakdown
        """
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        commission_amount = transaction_amount * platform_commission
        seller_earnings = transaction_amount - commission_amount

        return {
            'transaction_amount': transaction_amount,
            'platform_commission_rate': platform_commission,
            'commission_amount': commission_amount,
            'seller_earnings': seller_earnings,
            'net_percentage': (seller_earnings / transaction_amount) * 100 if transaction_amount != 0 else 0
        }

    def process_transaction_earnings(self, seller_id: int, transaction_amount: float, transaction_id: int = None) -> Earning:
        """
        Process earnings from a successful transaction

        Args:
            seller_id: ID of the seller
            transaction_amount: Amount of the transaction
            transaction_id: Optional transaction ID for reference

        Returns:
            Created earning record
        """
        earnings_breakdown = self.calculate_seller_earnings(seller_id, transaction_amount)

        # Create earning record for seller
        earning = Earning(
            EarningID=None,
            UserID=seller_id,
            TotalAmount=earnings_breakdown['seller_earnings'],
            Date=datetime.now()
        )

        created_earning = self.earning_repository.add(earning)

        logger.info(f"Processed earnings for seller {seller_id}: ${earnings_breakdown['seller_earnings']:.2f} from transaction ${transaction_amount:.2f}")

        return created_earning

    def get_earnings_statistics(self, user_id: int) -> Dict[str, Any]:
        """
        Get comprehensive earnings statistics for a user

        Args:
            user_id: User ID to get statistics for

        Returns:
            Dict with earnings statistics
        """
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        # Get all earnings
        all_earnings = self.earning_repository.get_by_user_id(user_id)

        if not all_earnings:
            return {
                'user_id': user_id,
                'total_earnings': 0.0,
                'total_transactions': 0,
                'average_earning': 0.0,
                'monthly_earnings': {},
                'recent_earnings': [],
                'earnings_trend': 'neutral'
            }

        # Calculate basic statistics
        total_earnings = sum(e.TotalAmount for e in all_earnings)
        total_transactions = len(all_earnings)
        average_earning = total_earnings / total_transactions

        # Monthly breakdown (last 12 months)
        monthly_earnings = {}
        twelve_months_ago = datetime.now() - timedelta(days=365)

        for earning in all_earnings:
            if earning.Date >= twelve_months_ago:
                month_key = earning.Date.strftime('%Y-%m')
                if month_key not in monthly_earnings:
                    monthly_earnings[month_key] = {'amount': 0.0, 'count': 0}
                monthly_earnings[month_key]['amount'] += earning.TotalAmount
                monthly_earnings[month_key]['count'] += 1

        # Recent earnings (last 10)
        recent_earnings = sorted(all_earnings, key=lambda x: x.Date, reverse=True)[:10]
        recent_earnings_data = []
        for earning in recent_earnings:
            recent_earnings_data.append({
                'earning_id': earning.EarningID,
                'amount': earning.TotalAmount,
                'date': earning.Date.isoformat()
            })

        # Calculate trend (last 30 days vs previous 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        sixty_days_ago = datetime.now() - timedelta(days=60)

        recent_earnings_amount = sum(e.TotalAmount for e in all_earnings if e.Date >= thirty_days_ago)
        previous_earnings_amount = sum(e.TotalAmount for e in all_earnings if sixty_days_ago <= e.Date < thirty_days_ago)

        trend = 'neutral'
        if previous_earnings_amount > 0:
            change_percentage = ((recent_earnings_amount - previous_earnings_amount) / previous_earnings_amount) * 100
        else:
            change_percentage = 0
            if change_percentage > 10:
                trend = 'increasing'
            elif change_percentage < -10:
                trend = 'decreasing'

        return {
            'user_id': user_id,
            'total_earnings': round(total_earnings, 2),
            'total_transactions': total_transactions,
            'average_earning': round(average_earning, 2),
            'monthly_earnings': monthly_earnings,
            'recent_earnings': recent_earnings_data,
            'earnings_trend': trend,
            'recent_period_earnings': round(recent_earnings_amount, 2),
            'previous_period_earnings': round(previous_earnings_amount, 2)
        }

    def get_earnings_summary(self, user_id: int, period: str = 'all') -> Dict[str, Any]:
        """
        Get earnings summary for different time periods

        Args:
            user_id: User ID
            period: Time period ('all', 'year', 'month', 'week')

        Returns:
            Dict with earnings summary
        """
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        # Calculate date range based on period
        end_date = datetime.now()
        if period == 'week':
            start_date = end_date - timedelta(days=7)
        elif period == 'month':
            start_date = end_date - timedelta(days=30)
        elif period == 'year':
            start_date = end_date - timedelta(days=365)
        else:  # 'all'
            start_date = datetime.min

        # Get earnings for the period
        if period == 'all':
            earnings = self.earning_repository.get_by_user_id(user_id)
        else:
            earnings = self.earning_repository.get_earnings_by_date_range(user_id, start_date, end_date)

        if not earnings:
            return {
                'user_id': user_id,
                'period': period,
                'total_amount': 0.0,
                'transaction_count': 0,
                'average_amount': 0.0,
                'highest_earning': 0.0,
                'lowest_earning': 0.0
            }

        amounts = [e.TotalAmount for e in earnings]

        return {
            'user_id': user_id,
            'period': period,
            'total_amount': round(sum(amounts), 2),
            'transaction_count': len(earnings),
            'average_amount': round(sum(amounts) / len(amounts), 2),
            'highest_earning': round(max(amounts), 2),
            'lowest_earning': round(min(amounts), 2),
            'start_date': start_date.isoformat() if start_date != datetime.min else None,
            'end_date': end_date.isoformat()
        }
