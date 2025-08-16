from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean, func
from infrastructure.databases.base import Base

class NotificationModel(Base):
    __tablename__ = "notifications"

    NotificationID = Column(Integer, primary_key=True, autoincrement=True)
    UserID = Column(Integer, ForeignKey("users.UserId"), nullable=False)  # người nhận thông báo
    Content = Column(String(1000), nullable=False)
    IsRead = Column(Boolean, default=False, nullable=False)  # đã đọc hay chưa
    CreatedAt = Column(DateTime, server_default=func.now(), nullable=False)
