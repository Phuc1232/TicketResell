from domain.models.user import User
from domain.models.iuser_repository import IUserRepository
from typing import Optional, List
from datetime import datetime

class UserService:
    """
    User Service - Handles user profile management and CRUD operations
    Authentication logic moved to AuthService for better separation of concerns
    """

    def __init__(self, repository: IUserRepository):
        self.repository = repository

    def list_users(self) -> List[User]:
        return self.repository.list()

    def get_user(self, user_id: int) -> Optional[User]:
        return self.repository.get_by_id(user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.repository.get_by_username(username)

    def update_user(self, user_id: int, phone_number: str, username: str, status: str,
                    date_of_birth, role_id: int) -> User:
        user = User(id=user_id, phone_number=phone_number, username=username, status=status,
                    password_hash=None, email=None, date_of_birth=date_of_birth,
                    create_date=None, role_id=role_id)
        return self.repository.update(user)

    def update_profile(self, user_id: int, **kwargs) -> User:
        """Update user profile with provided fields"""
        user = self.repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Update only provided fields
        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        
        return self.repository.update(user)

    def search_users(self, query: str = '', verified: str = None, min_rating: str = None, status: str = None) -> List[User]:
        """Search users by criteria"""
        # For now, return all users. This can be enhanced with actual search logic
        return self.repository.list()

    def verify_user(self, user_id: int, verification_code: str, verification_type: str) -> User:
        """Verify user account"""
        user = self.repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        # For now, just return the user. Verification logic can be added later
        return user

    def rate_user(self, current_user_id: int, target_user_id: int, rating: float, comment: str = None, transaction_id: int = None) -> User:
        """Rate another user"""
        user = self.repository.get_by_id(target_user_id)
        if not user:
            raise ValueError("User not found")
        # For now, just return the user. Rating logic can be added later
        return user

    def delete_user(self, user_id: int) -> None:
        self.repository.delete(user_id)
