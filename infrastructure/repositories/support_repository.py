from typing import List, Optional
from domain.models.support import Support
from domain.models.isupport_repository import ISupportRepository
from infrastructure.models.support_model import SupportModel
from datetime import datetime

class SupportRepository(ISupportRepository):
    def __init__(self, session=None):
        if session is None:
            from infrastructure.databases.mssql import session as default_session
            self.session = default_session
        else:
            self.session = session

    def add(self, support: Support) -> Support:
        model = SupportModel(
            UserID=support.UserID,
            Status=support.Status,
            Create_at=support.Create_at,
            Updated_at=support.Updated_at,
            Issue_des=support.Issue_des,
            Title=support.Title,
            RecipientType=support.RecipientType,
            RecipientID=support.RecipientID
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_domain(model)
    
    def get_by_id(self, support_id: int) -> Optional[Support]:
        model = self.session.query(SupportModel).filter(SupportModel.SupportID == support_id).first()
        return self._to_domain(model) if model else None
    
    def get_by_user_id(self, user_id: int) -> List[Support]:
        models = self.session.query(SupportModel).filter(SupportModel.UserID == user_id).order_by(SupportModel.Create_at.desc()).all()
        return [self._to_domain(model) for model in models]
    
    def update(self, support: Support) -> Support:
        model = self.session.query(SupportModel).filter(SupportModel.SupportID == support.SupportID).first()
        if model:
            model.UserID = support.UserID
            model.Status = support.Status
            model.Updated_at = datetime.now()
            model.Issue_des = support.Issue_des
            model.Title = support.Title
            self.session.commit()
            self.session.refresh(model)
            return self._to_domain(model)
        return None
    
    def delete(self, support_id: int) -> bool:
        model = self.session.query(SupportModel).filter(SupportModel.SupportID == support_id).first()
        if model:
            self.session.delete(model)
            self.session.commit()
            return True
        return False
    
    def get_by_status(self, status: str) -> List[Support]:
        models = self.session.query(SupportModel).filter(SupportModel.Status == status).order_by(SupportModel.Create_at.desc()).all()
        return [self._to_domain(model) for model in models]
    
    def get_all(self) -> List[Support]:
        models = self.session.query(SupportModel).order_by(SupportModel.Create_at.desc()).all()
        return [self._to_domain(model) for model in models]
    
    def update_status(self, support_id: int, status: str) -> bool:
        model = self.session.query(SupportModel).filter(SupportModel.SupportID == support_id).first()
        if model:
            model.Status = status
            model.Updated_at = datetime.now()
            self.session.commit()
            return True
        return False
    
    def _to_domain(self, model: SupportModel) -> Support:
        return Support(
            SupportID=model.SupportID,
            UserID=model.UserID,
            Status=model.Status,
            Create_at=model.Create_at,
            Updated_at=model.Updated_at,
            Issue_des=model.Issue_des,
            Title=model.Title,
            RecipientType=model.RecipientType,
            RecipientID=model.RecipientID
        )
