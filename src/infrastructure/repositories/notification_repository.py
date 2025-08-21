from typing import List, Optional
from domain.models.notification import Notification
from domain.models.inotification_repository import INotificationRepository
from infrastructure.models.notification_model import NotificationModel
from datetime import datetime

class NotificationRepository(INotificationRepository):
    def __init__(self, session=None):
        if session is None:
            from infrastructure.databases.mssql import session as default_session
            self.session = default_session
        else:
            self.session = session
    def add(self, notification: Notification) -> Notification:
        model = NotificationModel(
            UserID=notification.UserID,
            Title=notification.Title,
            Content=notification.Content,
            Type=notification.Type,
            IsRead=notification.IsRead,
            CreatedAt=notification.CreatedAt,
            ReadAt=notification.ReadAt
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_domain(model)
    
    def get_by_id(self, notification_id: int) -> Optional[Notification]:
        model = self.session.query(NotificationModel).filter(NotificationModel.NotificationID == notification_id).first()
        return self._to_domain(model) if model else None
    
    def get_by_user_id(self, user_id: int, limit: int = 20, offset: int = 0, unread_only: bool = False) -> List[Notification]:
        query = self.session.query(NotificationModel).filter(NotificationModel.UserID == user_id)
        
        if unread_only:
            query = query.filter(NotificationModel.IsRead == False)
        
        models = query.order_by(NotificationModel.CreatedAt.desc()).offset(offset).limit(limit).all()
        return [self._to_domain(model) for model in models]
    
    def mark_as_read(self, notification_id: int) -> bool:
        model = self.session.query(NotificationModel).filter(NotificationModel.NotificationID == notification_id).first()
        if model:
            model.IsRead = True
            model.ReadAt = datetime.now()
            self.session.commit()
            return True
        return False
    
    def mark_all_as_read(self, user_id: int) -> bool:
        notifications = self.session.query(NotificationModel).filter(
            (NotificationModel.UserID == user_id) & (NotificationModel.IsRead == False)
        ).all()

        for notification in notifications:
            notification.IsRead = True
            notification.ReadAt = datetime.now()

        self.session.commit()
        return True
    
    def get_unread_count(self, user_id: int) -> int:
        return self.session.query(NotificationModel).filter(
            (NotificationModel.UserID == user_id) & (NotificationModel.IsRead == False)
        ).count()
    
    def delete(self, notification_id: int) -> bool:
        model = self.session.query(NotificationModel).filter(NotificationModel.NotificationID == notification_id).first()
        if model:
            self.session.delete(model)
            self.session.commit()
            return True
        return False

    def delete_older_than(self, cutoff_date) -> int:
        from datetime import datetime
        deleted_count = self.session.query(NotificationModel).filter(
            NotificationModel.CreatedAt < cutoff_date
        ).delete()
        self.session.commit()
        return deleted_count

    def get_by_type(self, user_id: int, notification_type: str, limit: int = 20, offset: int = 0) -> List[Notification]:
        models = self.session.query(NotificationModel).filter(
            NotificationModel.UserID == user_id,
            NotificationModel.Type == notification_type
        ).order_by(NotificationModel.CreatedAt.desc()).offset(offset).limit(limit).all()
        return [self._to_domain(model) for model in models]

    def _to_domain(self, model: NotificationModel) -> Notification:
        return Notification(
            NotificationID=model.NotificationID,
            UserID=model.UserID,
            Title=model.Title,
            Content=model.Content,
            Type=model.Type,
            IsRead=model.IsRead,
            CreatedAt=model.CreatedAt,
            ReadAt=model.ReadAt
        )
