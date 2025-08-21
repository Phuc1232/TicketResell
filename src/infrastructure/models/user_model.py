from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float, Text
from infrastructure.databases.base import Base

class UserModel(Base):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}  # Cho phép ghi đè nếu đã khai báo trước

    UserId = Column(Integer, primary_key=True, autoincrement=True)
    Phone_Number = Column(String(15), nullable=False)
    UserName = Column(String(50), nullable=False)
    Status = Column(String(20), default='active')
    Password = Column(String(255), nullable=False)
    Email = Column(String(100), nullable=False, unique=True)
    Date_Of_Birth = Column(DateTime, nullable=False)
    Create_Date = Column(DateTime)
    RoleID = Column(Integer, ForeignKey('roles.RoleID'), nullable=False)

    # Verification fields
    verified = Column(Boolean, default=False, nullable=False)
    verification_code = Column(String(6), nullable=True)
    verification_expires_at = Column(DateTime, nullable=True)
