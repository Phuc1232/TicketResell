from abc import ABC, abstractmethod
from typing import Optional, List
from .user import User

class IUserRepository(ABC):
    @abstractmethod
    def add(self, user: User) -> User:
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        pass

    @abstractmethod
    def update(self, user: User) -> User:
        pass
    
    @abstractmethod
    def list(self) -> List[User]:
        pass

    @abstractmethod
    def delete(self, user_id: int) -> None:
        pass