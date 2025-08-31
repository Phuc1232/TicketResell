from typing import List, Optional
from domain.models.earning import Earning
from domain.models.iearning_repository import IEarningRepository
from infrastructure.models.earning_model import EarningModel
from datetime import datetime
from sqlalchemy import func

class EarningRepository(IEarningRepository):
    def __init__(self, session=None):
        if session is None:
            from infrastructure.databases.mssql import session as default_session
            self.session = default_session
        else:
            self.session = session

    def add(self, earning: Earning) -> Earning:
        try:
            model = EarningModel(
                UserID=earning.UserID,
                TotalAmount=earning.TotalAmount,
                Date=earning.Date
            )
            self.session.add(model)
            self.session.commit()
            self.session.refresh(model)
            return self._to_domain(model)
        except Exception as e:
            self.session.rollback()
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error adding earning for user {earning.UserID}: {str(e)}")
            raise
    
    def get_by_id(self, earning_id: int) -> Optional[Earning]:
        model = self.session.query(EarningModel).filter(EarningModel.EarningID == earning_id).first()
        return self._to_domain(model) if model else None
    
    def get_by_user_id(self, user_id: int) -> List[Earning]:
        models = self.session.query(EarningModel).filter(EarningModel.UserID == user_id).order_by(EarningModel.Date.desc()).all()
        return [self._to_domain(model) for model in models]
    
    def update(self, earning: Earning) -> Earning:
        try:
            model = self.session.query(EarningModel).filter(EarningModel.EarningID == earning.EarningID).first()
            if not model:
                raise ValueError("Earning not found")
            
            model.UserID = earning.UserID
            model.TotalAmount = earning.TotalAmount
            model.Date = earning.Date
            self.session.commit()
            self.session.refresh(model)
            return self._to_domain(model)
        except Exception as e:
            self.session.rollback()
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error updating earning {earning.EarningID}: {str(e)}")
            raise
    
    def delete(self, earning_id: int) -> bool:
        try:
            model = self.session.query(EarningModel).filter(EarningModel.EarningID == earning_id).first()
            if model:
                self.session.delete(model)
                self.session.commit()
                return True
            return False
        except Exception as e:
            self.session.rollback()
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error deleting earning {earning_id}: {str(e)}")
            raise
    
    def get_total_earnings_by_user(self, user_id: int) -> float:
        result = self.session.query(func.sum(EarningModel.TotalAmount)).filter(EarningModel.UserID == user_id).scalar()
        return result if result else 0.0
    
    def get_earnings_by_date_range(self, user_id: int, start_date, end_date) -> List[Earning]:
        models = self.session.query(EarningModel).filter(
            EarningModel.UserID == user_id,
            EarningModel.Date >= start_date,
            EarningModel.Date <= end_date
        ).order_by(EarningModel.Date.desc()).all()
        return [self._to_domain(model) for model in models]
    
    def _to_domain(self, model: EarningModel) -> Earning:
        return Earning(
            EarningID=model.EarningID,
            UserID=model.UserID,
            TotalAmount=model.TotalAmount,
            Date=model.Date
        )
