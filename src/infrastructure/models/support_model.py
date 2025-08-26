from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from infrastructure.databases.base import Base

class SupportModel(Base):
    __tablename__ = 'support'
    __table_args__ = {'extend_existing': True}

    SupportID = Column(Integer, primary_key=True, autoincrement=True)
    UserID = Column(Integer, ForeignKey('users.UserId'), nullable=False)
    Status = Column(String(20), default='open')  # open, in_progress, resolved, closed
    Create_at = Column(DateTime, default=func.now())
    Updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    Issue_des = Column(Text)  # Description of the issue
    Title = Column(String(200), nullable=False)  # Title of the support ticket
    RecipientType = Column(String(20), nullable=False, default='user') # 'user' or 'admin'
    RecipientID = Column(Integer, nullable=True) # ID of the recipient (admin_id or user_id)
