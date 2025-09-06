from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from infrastructure.databases.base import Base

class MessageModel(Base):
    __tablename__ = 'messages'
    __table_args__ = {'extend_existing': True}

    MessageID = Column(Integer, primary_key=True, autoincrement=True)
    SenderID = Column(Integer, ForeignKey('users.UserId'), nullable=False)
    ReceiverID = Column(Integer, ForeignKey('users.UserId'), nullable=False)
    Content = Column(String(1000), nullable=False)
    TicketID = Column(Integer, ForeignKey('ticket.TicketID'))
    IsRead = Column(Boolean, default=False)
    SentAt = Column(DateTime, default=func.now())
    ReadAt = Column(DateTime)
