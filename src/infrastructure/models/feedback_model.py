from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from infrastructure.databases.base import Base

class FeedbackModel(Base):
    __tablename__ = 'feedback'
    __table_args__ = {'extend_existing': True}

    FeedBackID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    TransactionID = Column(Integer, ForeignKey('transactions.TransactionID'), nullable=False)
    SenderID = Column(Integer, ForeignKey('users.UserId'), nullable=False)
    ReceiverID = Column(Integer, ForeignKey('users.UserId'), nullable=False)
    Rating = Column(Float, nullable=False)
    Date = Column(DateTime, nullable=False)
    Comment = Column(String(255), nullable=True)  # cho phép null

