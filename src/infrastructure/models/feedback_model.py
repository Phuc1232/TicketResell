from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text
from sqlalchemy.sql import func
from infrastructure.databases.base import Base

class UserFeedbackModel(Base):
    __tablename__ = 'user_feedback'
    __table_args__ = {'extend_existing': True}

    FeedbackID = Column(Integer, primary_key=True, autoincrement=True)
    ReviewerID = Column(Integer, ForeignKey('users.UserId'), nullable=False)
    TargetUserID = Column(Integer, ForeignKey('users.UserId'), nullable=False)
    Rating = Column(Float, nullable=False)
    Comment = Column(Text)
    TransactionID = Column(Integer, ForeignKey('transactions.TransactionID'))
    CreatedAt = Column(DateTime, default=func.now())

class TicketFeedbackModel(Base):
    __tablename__ = 'ticket_feedback'
    __table_args__ = {'extend_existing': True}

    FeedbackID = Column(Integer, primary_key=True, autoincrement=True)
    ReviewerID = Column(Integer, ForeignKey('users.UserId'), nullable=False)
    TicketID = Column(Integer, ForeignKey('ticket.TicketID'), nullable=False)
    Rating = Column(Float, nullable=False)
    Comment = Column(Text)
    CreatedAt = Column(DateTime, default=func.now())

