from sqlalchemy import Column, Integer, String
from infrastructure.databases.base import Base

class RoleModel(Base):
    __tablename__ = 'roles'
    __table_args__ = {'extend_existing': True}

    RoleID = Column(Integer, primary_key=True, autoincrement=True)
    RoleName = Column(String(50), nullable=False, unique=True)
