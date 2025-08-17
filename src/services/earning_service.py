from typing import List, Optional
from domain.models.earning import Earning
from domain.models.iearning_repository import IEarningRepository
from domain.models.iuser_repository import IUserRepository
from datetime import datetime

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
