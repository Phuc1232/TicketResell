from typing import Optional, Dict, Any
from domain.models.user import User
from domain.models.iuser_repository import IUserRepository
from services.email_service import EmailService
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token
from utils.jwt_helpers import create_jwt_identity
from datetime import datetime, timedelta
import random
import string
import logging

# Custom exceptions for better error handling
class VerificationCodeExpiredError(ValueError):
    """Raised when verification code has expired"""
    pass

class VerificationCodeInvalidError(ValueError):
    """Raised when verification code is invalid"""
    pass

class UserAlreadyVerifiedError(ValueError):
    """Raised when user is already verified"""
    pass

logger = logging.getLogger(__name__)

class AuthService:
    """
    Authentication Service - Handles all authentication-related operations
    Including user registration, verification, login, and password management
    """
    
    def __init__(self, user_repository: IUserRepository, email_service: Optional[EmailService] = None):
        self.user_repository = user_repository
        self.email_service = email_service or EmailService()
    
    def register_user(self, username: str, email: str, password: str,
                     phone_number: str, date_of_birth, **kwargs) -> Dict[str, Any]:
        """
        Register a new user with email verification
        
        Args:
            username: User's username
            email: User's email address
            password: Plain text password
            phone_number: User's phone number
            date_of_birth: User's date of birth
            **kwargs: Additional user data
            
        Returns:
            Dict with registration status and message
            
        Raises:
            ValueError: If user already exists or validation fails
        """
        # Check if user already exists
        existing_user = self.user_repository.get_by_email(email)
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Hash password
        password_hash = generate_password_hash(password)
        
        # Generate verification code
        verification_code = self._generate_verification_code()
        verification_expires_at = datetime.utcnow() + timedelta(minutes=5)

        # Get default user role ID (fixed ID = 2)
        default_role_id = self._get_default_user_role_id()

        # Create user with unverified status
        user = User(
            id=None,
            phone_number=phone_number,
            username=username,
            status='active',
            password_hash=password_hash,
            email=email,
            date_of_birth=date_of_birth,
            create_date=datetime.utcnow(),
            role_id=kwargs.get('role_id', default_role_id),  # Use auto-created role
            verified=False,
            verification_code=verification_code,
            verification_expires_at=verification_expires_at
        )
        
        # Save user to database
        created_user = self.user_repository.add(user)
        
        # Send verification email
        email_sent = self.email_service.send_verification_email(
            to_email=email,
            username=username,
            verification_code=verification_code
        )
        
        if not email_sent:
            logger.warning(f"Failed to send verification email to {email}")

        # Generate temporary JWT token for verification process
        temp_token = create_access_token(
            identity=create_jwt_identity(created_user.id, created_user.role_id, created_user.username),
            expires_delta=timedelta(minutes=10)  # Short-lived token for verification
        )

        # Prepare response message
        message = 'Registration successful, please check your email for verification code'
        if self.email_service.debug_mode:
            message ='Registration successful, but debug mode'

        response = {
            'user_id': created_user.id,
            'email': created_user.email,
            'username': created_user.username,
            'verified': created_user.verified,
            'temp_token': temp_token,  # For verification endpoint
            'message': message
        }

        # In debug mode, include verification code in response
        if self.email_service.debug_mode:
            response['verification_code'] = verification_code

        return response
    
    def verify_user(self, user_id: int, verification_code: str) -> Dict[str, Any]:
        """
        Verify user account with verification code
        
        Args:
            user_id: User ID from JWT token
            verification_code: 6-digit verification code
            
        Returns:
            Dict with verification status and tokens
            
        Raises:
            ValueError: If verification fails
        """
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        if user.verified:
            raise UserAlreadyVerifiedError("User is already verified")

        if not user.verification_code:
            raise ValueError("No verification code found for this user")

        # Check if code has expired BEFORE checking if it's correct
        if user.verification_expires_at and datetime.utcnow() > user.verification_expires_at:
            raise VerificationCodeExpiredError("Verification code has expired")

        if user.verification_code != verification_code:
            raise VerificationCodeInvalidError("Invalid verification code")
        
        # Update user as verified and clear verification data
        user.verified = True
        user.verification_code = None
        user.verification_expires_at = None
        
        updated_user = self.user_repository.update(user)
        
        # Generate full access tokens with role information
        jwt_identity = create_jwt_identity(updated_user.id, updated_user.role_id, updated_user.username)
        access_token = create_access_token(
            identity=jwt_identity,
            expires_delta=timedelta(hours=24)
        )
        refresh_token = create_refresh_token(
            identity=jwt_identity,
            expires_delta=timedelta(days=30)
        )
        
        return {
            'user': updated_user,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'message': 'User verified successfully'
        }
    
    def resend_verification_code(self, user_id: int) -> Dict[str, str]:
        """
        Resend verification code to user
        
        Args:
            user_id: User ID
            
        Returns:
            Dict with status message
            
        Raises:
            ValueError: If user not found or already verified
        """
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        if user.verified:
            raise UserAlreadyVerifiedError("User is already verified")
        
        # Generate new verification code
        verification_code = self._generate_verification_code()
        verification_expires_at = datetime.utcnow() + timedelta(minutes=5)
        
        # Update user with new verification code
        user.verification_code = verification_code
        user.verification_expires_at = verification_expires_at
        
        self.user_repository.update(user)
        
        # Send new verification email
        email_sent = self.email_service.send_verification_email(
            to_email=user.email,
            username=user.username,
            verification_code=verification_code
        )

        if not email_sent:
            logger.warning(f"Failed to resend verification email to {user.email}")
            # In debug mode, don't fail - just log the issue
            if not self.email_service.debug_mode:
                raise ValueError("Failed to send verification email")

        message = 'Verification code resent successfully'
        if self.email_service.debug_mode:
            message += ' (Debug mode - email simulated)'

        return {
            'message': message,
            'verification_code': verification_code if self.email_service.debug_mode else None
        }
    
    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user and return tokens
        
        Args:
            email: User's email
            password: User's password
            
        Returns:
            Dict with user info and tokens
            
        Raises:
            ValueError: If authentication fails
        """
        user = self.user_repository.get_by_email(email)
        
        if not user:
            raise ValueError("Invalid email or password")
        
        if not check_password_hash(user.password_hash, password):
            raise ValueError("Invalid email or password")
        
        if user.status != 'active':
            raise ValueError("Account is not active")
        
        # Check if user is verified
        if not user.verified:
            # Return special error code for unverified accounts
            raise ValueError("ACCOUNT_NOT_VERIFIED")
        
        # Generate tokens with role information
        jwt_identity = create_jwt_identity(user.id, user.role_id, user.username)
        access_token = create_access_token(
            identity=jwt_identity,
            expires_delta=timedelta(hours=24)
        )
        refresh_token = create_refresh_token(
            identity=jwt_identity,
            expires_delta=timedelta(days=30)
        )
        
        return {
            'user': user,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'message': 'Login successful'
        }
    
    def refresh_token(self, user_id: str) -> Dict[str, str]:
        """
        Generate new access token from refresh token
        
        Args:
            user_id: User ID from refresh token
            
        Returns:
            Dict with new access token
            
        Raises:
            ValueError: If user not found or inactive
        """
        user = self.user_repository.get_by_id(int(user_id))
        if not user or user.status != 'active' or not user.verified:
            raise ValueError("Invalid user or inactive account")
        
        # Create new access token with role information
        jwt_identity = create_jwt_identity(user.id, user.role_id, user.username)
        access_token = create_access_token(
            identity=jwt_identity,
            expires_delta=timedelta(hours=24)
        )
        
        return {
            'access_token': access_token,
            'token_type': 'Bearer'
        }
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """
        Change user password after verifying old password
        
        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password
            
        Returns:
            bool: True if successful
            
        Raises:
            ValueError: If validation fails
        """
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        if not check_password_hash(user.password_hash, old_password):
            raise ValueError("Current password is incorrect")
        
        # Update password
        user.password_hash = generate_password_hash(new_password)
        self.user_repository.update(user)
        
        return True
    
    def _get_default_user_role_id(self) -> int:
        """
        Get default user role ID (fixed ID = 2)

        Returns:
            int: Default user role ID

        Raises:
            ValueError: If User role doesn't exist in database
        """
        try:
            from infrastructure.models.role_model import RoleModel
            from infrastructure.databases.mssql import session

            # Check if User role (ID=2) exists
            user_role = session.query(RoleModel).filter(RoleModel.RoleID == 2).first()
            if user_role:
                return 2

            # If role doesn't exist, raise error with helpful message
            raise ValueError(
                "User role (ID=2) not found in database. "
                "Please run role seeding script: python src/database/seed_roles.py"
            )

        except Exception as e:
            logger.error(f"Error getting default user role: {e}")
            raise ValueError(
                "Failed to get default user role. "
                "Please ensure roles are properly seeded in database."
            )

    def _generate_verification_code(self) -> str:
        """
        Generate a random 6-digit verification code

        Returns:
            str: 6-digit verification code
        """
        return ''.join(random.choices(string.digits, k=6))
