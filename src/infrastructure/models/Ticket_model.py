from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from infrastructure.databases.base import Base

class TicketModel(Base):
    __tablename__ = 'ticket'
    __table_args__ = {'extend_existing': True}  # Cho phép ghi đè nếu đã tồn tại

    # Các thuộc tính theo ERD
    TicketID = Column(Integer, primary_key=True, autoincrement=True)
    EventDate = Column(DateTime, nullable=False)
    Price = Column(Float, nullable=False)
    EventName = Column(String(100), nullable=False)
    Status = Column(String(20), default='Available')
    PaymentMethod = Column(String(100), nullable=False)  # Cash, Bank Transfer, Digital Wallet, Credit Card
    ContactInfo = Column(String(200), nullable=False)
    OwnerID = Column(Integer, ForeignKey('users.UserId'), nullable=False)

