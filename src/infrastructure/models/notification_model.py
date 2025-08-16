from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from infrastructure.databases.base import Base

class NotificationModel(Base):
    __tablename__ = 'notifications'
    __table_args__ = {'extend_existing': True}

    NotificationID = Column(Integer, primary_key=True, autoincrement=True)
    UserID = Column(Integer, ForeignKey('users.UserId'), nullable=False)
    Title = Column(String(200), nullable=False)
    Content = Column(String(500), nullable=False)
    Type = Column(String(50), nullable=False)  # ticket_reminder, price_alert, chat_message, payment_confirmation, system
    IsRead = Column(Boolean, default=False)
    CreatedAt = Column(DateTime, default=func.now())
    ReadAt = Column(DateTime)
