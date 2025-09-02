"""
Admin Seed Script - Tạo tài khoản admin mặc định cho TicketResell
"""

import sys
import os
import logging
from datetime import datetime
from werkzeug.security import generate_password_hash

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from domain.models.user import User
from domain.models.iuser_repository import IUserRepository

logger = logging.getLogger(__name__)


class AdminSeeder:
    """
    Class để tạo admin user mặc định khi khởi chạy ứng dụng
    """
    
    # Admin user configuration
    ADMIN_CONFIG = {
        'username': 'admin',
        'email': 'thienphuc12a1ltt@gmail.com',
        'password': 'admin123',
        'phone_number': '0389027572',
        'date_of_birth': '1990-01-01T00:00:00Z',
        'role_id': 1,  # Admin role
        'verified': True,
        'status': 'active'
    }
    
    def __init__(self, user_repository: IUserRepository):
        """
        Initialize AdminSeeder với user repository
        
        Args:
            user_repository: Repository để thao tác với user data
        """
        self.user_repository = user_repository
    
    def _hash_password(self, password: str) -> str:
        """
        Hash password sử dụng Werkzeug (tương tự AuthService)

        Args:
            password: Plain text password

        Returns:
            Hashed password string
        """
        try:
            # Sử dụng cùng method như AuthService
            return generate_password_hash(password)
        except Exception as e:
            logger.error(f"Error hashing password: {e}")
            raise
    
    def _admin_exists(self) -> bool:
        """
        Kiểm tra admin user đã tồn tại chưa
        
        Returns:
            True nếu admin email đã tồn tại, False nếu chưa
        """
        try:
            existing_admin = self.user_repository.get_by_email(self.ADMIN_CONFIG['email'])
            return existing_admin is not None
        except Exception as e:
            logger.error(f"Error checking admin existence: {e}")
            return False
    
    def _create_admin_user(self) -> User:
        """
        Tạo admin user object với thông tin cấu hình
        
        Returns:
            User object đã được tạo
        """
        try:
            # Hash password
            hashed_password = self._hash_password(self.ADMIN_CONFIG['password'])
            
            # Parse date of birth
            date_of_birth = datetime.fromisoformat(
                self.ADMIN_CONFIG['date_of_birth'].replace('Z', '+00:00')
            )
            
            # Tạo User object (id=None sẽ được auto-generate bởi database)
            admin_user = User(
                id=None,  # Auto-generate by database
                phone_number=self.ADMIN_CONFIG['phone_number'],
                username=self.ADMIN_CONFIG['username'],
                status=self.ADMIN_CONFIG['status'],
                password_hash=hashed_password,
                email=self.ADMIN_CONFIG['email'],
                date_of_birth=date_of_birth,
                create_date=datetime.utcnow(),
                role_id=self.ADMIN_CONFIG['role_id'],
                verified=self.ADMIN_CONFIG['verified'],
                verification_code=None,  # Không cần verification
                verification_expires_at=None
            )
            
            return admin_user
            
        except Exception as e:
            logger.error(f"Error creating admin user object: {e}")
            raise

    def _ensure_roles_exist(self) -> bool:
        """
        Ensure required roles exist in database before creating admin

        Returns:
            bool: True if roles exist or created successfully
        """
        try:
            from database.seed_roles import seed_roles

            logger.info("Checking if roles exist...")
            success = seed_roles()

            if success:
                logger.info("Roles are properly seeded")
                return True
            else:
                logger.error("Failed to seed roles")
                return False

        except Exception as e:
            logger.error(f"Error ensuring roles exist: {e}")
            return False
    
    def seed_admin(self) -> bool:
        """
        Main method để seed admin user

        Returns:
            True nếu seed thành công hoặc admin đã tồn tại, False nếu thất bại
        """
        try:
            logger.info("Starting admin seed process...")

            # Ensure roles exist first
            self._ensure_roles_exist()

            # Kiểm tra admin đã tồn tại chưa
            if self._admin_exists():
                logger.info(f"Admin user already exists: {self.ADMIN_CONFIG['email']}")
                return True

            # Tạo admin user
            logger.info(f"Creating admin user: {self.ADMIN_CONFIG['email']}")
            admin_user = self._create_admin_user()

            # Lưu vào database
            created_admin = self.user_repository.add(admin_user)
            
            if created_admin:
                logger.info(f"Admin user created successfully!")
                logger.info(f"   Username: {created_admin.username}")
                logger.info(f"   Email: {created_admin.email}")
                logger.info(f"   Role ID: {created_admin.role_id}")
                logger.info(f"   Status: {created_admin.status}")
                logger.info(f"   Verified: {created_admin.verified}")
                logger.info(f"   Created at: {created_admin.create_date}")

                # Log login credentials
                logger.info("Admin login credentials:")
                logger.info(f"   Email: {self.ADMIN_CONFIG['email']}")
                logger.info(f"   Password: {self.ADMIN_CONFIG['password']}")

                return True
            else:
                logger.error("Failed to create admin user - repository returned None")
                return False

        except Exception as e:
            logger.error(f"Admin seed process failed: {e}")
            logger.exception("Full error traceback:")
            return False
    
    def get_admin_info(self) -> dict:
        """
        Lấy thông tin admin configuration để logging hoặc debugging
        
        Returns:
            Dict chứa admin config (không bao gồm password)
        """
        config = self.ADMIN_CONFIG.copy()
        config.pop('password', None)  # Remove password for security
        return config


def seed_default_admin(user_repository: IUserRepository) -> bool:
    """
    Convenience function để seed admin user
    
    Args:
        user_repository: User repository instance
        
    Returns:
        True nếu seed thành công, False nếu thất bại
    """
    try:
        seeder = AdminSeeder(user_repository)
        return seeder.seed_admin()
    except Exception as e:
        logger.error(f"Error in seed_default_admin: {e}")
        return False


def main():
    """
    Main function để test seed script độc lập
    """
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Import dependencies
        from infrastructure.repositories.user_repository import UserRepository
        from infrastructure.databases.mssql import session
        
        # Create repository
        user_repository = UserRepository(session)
        
        # Run seed
        success = seed_default_admin(user_repository)
        
        if success:
            print("Admin seed completed successfully!")
        else:
            print("Admin seed failed!")

    except Exception as e:
        logger.error(f"Error in main: {e}")
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
