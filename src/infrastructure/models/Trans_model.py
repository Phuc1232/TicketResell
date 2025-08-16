from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from infrastructure.databases.base import Base

class TransactionModel(Base):
    __tablename__ = 'transactions'
    __table_args__ = {'extend_existing': True}  # Cho phép ghi đè nếu đã tồn tại

    TransactionID = Column(Integer, primary_key=True, autoincrement=True)
    PaymentStatus = Column(String(20),nullable=False)
    PaymentDate = Column(DateTime,nullable=False)
    SellerID = Column(Integer, ForeignKey('users.UserId'),nullable=False)
    BuyerID = Column(Integer, ForeignKey('users.UserId'),nullable=False)
    TicketID = Column(Integer, ForeignKey('ticket.TicketID'),nullable=False)

