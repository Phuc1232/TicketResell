"""
Role seeding script to ensure consistent role management
"""

import logging
from typing import List, Dict, Any
from infrastructure.models.role_model import RoleModel
from infrastructure.databases.mssql import session

logger = logging.getLogger(__name__)

class RoleSeeder:
    """
    Class to manage role seeding and ensure consistent role data
    """
    
    # Predefined roles with fixed IDs
    DEFAULT_ROLES = [
        {'RoleID': 1, 'RoleName': 'Admin'},
        {'RoleID': 2, 'RoleName': 'User'},
    ]
    
    def __init__(self, db_session=None):
        """
        Initialize RoleSeeder with database session
        
        Args:
            db_session: Database session (uses default if None)
        """
        self.session = db_session or session
    
    def _role_exists(self, role_id: int) -> bool:
        """
        Check if a role with specific ID exists
        
        Args:
            role_id: Role ID to check
            
        Returns:
            bool: True if role exists
        """
        try:
            role = self.session.query(RoleModel).filter(RoleModel.RoleID == role_id).first()
            return role is not None
        except Exception as e:
            logger.error(f"Error checking role existence: {e}")
            return False
    
    def _create_role(self, role_data: Dict[str, Any]) -> bool:
        """
        Create a single role
        
        Args:
            role_data: Dictionary containing RoleID and RoleName
            
        Returns:
            bool: True if successful
        """
        try:
            # Check if role already exists
            if self._role_exists(role_data['RoleID']):
                logger.info(f"Role already exists: {role_data['RoleName']} (ID: {role_data['RoleID']})")
                return True

            # Create new role with explicit ID
            role = RoleModel(
                RoleID=role_data['RoleID'],
                RoleName=role_data['RoleName']
            )

            self.session.add(role)
            self.session.commit()

            logger.info(f"Created role: {role_data['RoleName']} (ID: {role_data['RoleID']})")
            return True

        except Exception as e:
            logger.error(f"Error creating role {role_data['RoleName']}: {e}")
            self.session.rollback()
            return False
    
    def seed_default_roles(self) -> bool:
        """
        Seed all default roles
        
        Returns:
            bool: True if all roles created successfully
        """
        try:
            logger.info("Starting role seeding process...")

            success_count = 0
            total_roles = len(self.DEFAULT_ROLES)

            for role_data in self.DEFAULT_ROLES:
                if self._create_role(role_data):
                    success_count += 1

            if success_count == total_roles:
                logger.info(f"All {total_roles} roles seeded successfully!")
                return True
            else:
                logger.warning(f"Only {success_count}/{total_roles} roles seeded successfully")
                return False

        except Exception as e:
            logger.error(f"Error in role seeding process: {e}")
            return False
    
    def get_role_by_name(self, role_name: str) -> int:
        """
        Get role ID by role name
        
        Args:
            role_name: Name of the role
            
        Returns:
            int: Role ID or None if not found
        """
        try:
            role = self.session.query(RoleModel).filter(RoleModel.RoleName == role_name).first()
            return role.RoleID if role else None
        except Exception as e:
            logger.error(f"Error getting role by name: {e}")
            return None
    
    def get_default_user_role_id(self) -> int:
        """
        Get the default role ID for regular users
        
        Returns:
            int: Default user role ID (2)
        """
        return 2  # Fixed ID for User role
    
    def get_admin_role_id(self) -> int:
        """
        Get the admin role ID
        
        Returns:
            int: Admin role ID (1)
        """
        return 1  # Fixed ID for Admin role
    
    def verify_role_integrity(self) -> Dict[str, Any]:
        """
        Verify role system integrity
        
        Returns:
            dict: Integrity check results
        """
        try:
            results = {
                'total_roles': 0,
                'missing_roles': [],
                'existing_roles': [],
                'integrity_ok': True
            }
            
            # Check each default role
            for role_data in self.DEFAULT_ROLES:
                role_id = role_data['RoleID']
                role_name = role_data['RoleName']
                
                if self._role_exists(role_id):
                    results['existing_roles'].append(f"{role_name} (ID: {role_id})")
                else:
                    results['missing_roles'].append(f"{role_name} (ID: {role_id})")
                    results['integrity_ok'] = False
            
            results['total_roles'] = len(self.DEFAULT_ROLES)
            
            return results
            
        except Exception as e:
            logger.error(f"Error verifying role integrity: {e}")
            return {
                'total_roles': 0,
                'missing_roles': [],
                'existing_roles': [],
                'integrity_ok': False,
                'error': str(e)
            }

def seed_roles(db_session=None) -> bool:
    """
    Convenience function to seed roles
    
    Args:
        db_session: Database session (optional)
        
    Returns:
        bool: True if successful
    """
    seeder = RoleSeeder(db_session)
    return seeder.seed_default_roles()

def verify_roles(db_session=None) -> Dict[str, Any]:
    """
    Convenience function to verify role integrity
    
    Args:
        db_session: Database session (optional)
        
    Returns:
        dict: Verification results
    """
    seeder = RoleSeeder(db_session)
    return seeder.verify_role_integrity()

def main():
    """
    Main function for standalone execution
    """
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Seed roles
        success = seed_roles()

        if success:
            print("Role seeding completed successfully!")

            # Verify integrity
            results = verify_roles()
            print(f"\nRole Integrity Check:")
            print(f"Total roles: {results['total_roles']}")
            print(f"Existing roles: {len(results['existing_roles'])}")
            print(f"Missing roles: {len(results['missing_roles'])}")
            print(f"Integrity OK: {results['integrity_ok']}")

            if results['existing_roles']:
                print(f"\nExisting roles:")
                for role in results['existing_roles']:
                    print(f"  - {role}")

            if results['missing_roles']:
                print(f"\nMissing roles:")
                for role in results['missing_roles']:
                    print(f"  - {role}")
        else:
            print("Role seeding failed!")
            
    except Exception as e:
        logger.error(f"Error in main: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
