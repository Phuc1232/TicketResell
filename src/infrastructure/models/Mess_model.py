from sqlalchemy import Column, Integer, String, DateTime, ForeignKey,func
from infrastructure.databases.base import Base

class MessageModel(Base):
    __tablename__ = "messages"

    MessageID = Column(Integer, primary_key=True, autoincrement=True)
    SenderID = Column(Integer, ForeignKey("users.UserId"), nullable=False)
    ReceiverID = Column(Integer, ForeignKey("users.UserId"), nullable=False)
    Content = Column(String(1000), nullable=False)
    SentDate = Column(DateTime, server_default=func.now(), nullable=False)
