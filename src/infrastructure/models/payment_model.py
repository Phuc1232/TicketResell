from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.sql import func
from infrastructure.databases.base import Base

class PaymentModel(Base):
    __tablename__ = 'payment'
    __table_args__ = {'extend_existing': True}

    PaymentID = Column(Integer, primary_key=True, autoincrement=True)
    Methods = Column(String(100), nullable=False)  # Cash, Bank Transfer, Digital Wallet, Credit Card
    Status = Column(String(20), default='pending')  # pending, success, failed, cancelled
    Paid_at = Column(DateTime)
    amount = Column(Float, nullable=False)
    UserID = Column(Integer, ForeignKey('users.UserId'), nullable=False)
    Title = Column(String(200), nullable=False)
    TransactionID = Column(Integer, ForeignKey('transactions.TransactionID'))
