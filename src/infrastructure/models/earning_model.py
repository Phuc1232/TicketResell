from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.sql import func
from infrastructure.databases.base import Base

class EarningModel(Base):
    __tablename__ = 'earning'
    __table_args__ = {'extend_existing': True}

    EarningID = Column(Integer, primary_key=True, autoincrement=True)
    UserID = Column(Integer, ForeignKey('users.UserId'), nullable=False)
    TotalAmount = Column(Float, nullable=False, default=0.0)
    Date = Column(DateTime, default=func.now())
