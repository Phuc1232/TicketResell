from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.sql import func
from infrastructure.databases.base import Base

class TransactionModel(Base):
    __tablename__ = 'transactions'
    __table_args__ = {'extend_existing': True}

    TransactionID = Column(Integer, primary_key=True, autoincrement=True)
    TicketID = Column(Integer, ForeignKey('ticket.TicketID'), nullable=False)
    BuyerID = Column(Integer, ForeignKey('users.UserId'), nullable=False)
    SellerID = Column(Integer, ForeignKey('users.UserId'), nullable=False)
    Amount = Column(Float, nullable=False)
    PaymentMethod = Column(String(100), nullable=False)
    Status = Column(String(20), default='pending')  # pending, success, failed, cancelled
    PaymentTransactionID = Column(String(255))
    CreatedAt = Column(DateTime, default=func.now())
    UpdatedAt = Column(DateTime, default=func.now(), onupdate=func.now())
