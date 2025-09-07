"""
Comprehensive database setup script
Handles roles, admin user, and database integrity
"""

import logging
import sys
from typing import Dict, Any
from database.seed_roles import seed_roles, verify_roles
from database.seed_admin import seed_default_admin
#from database.fix_role_constraints import RoleConstraintFixer
from infrastructure.repositories.user_repository import UserRepository
from infrastructure.databases.mssql import session

logger = logging.getLogger(__name__)

class DatabaseSetup:
    """
    Complete database setup and maintenance
    """
    
    def __init__(self):
        """Initialize database setup"""
        self.user_repository = UserRepository(session)
        #self.constraint_fixer = RoleConstraintFixer(session)
    
    def setup_complete_database(self) -> Dict[str, Any]:
        """
        Complete database setup process
        
        Returns:
            dict: Setup results
        """
        try:
            logger.info("Starting complete database setup...")

            results = {
                'roles_setup': False,
                'admin_setup': False,
                'constraints_fixed': False,
                'verification_passed': False,
                'success': False,
                'errors': []
            }

            # Step 1: Setup roles
            logger.info("Step 1: Setting up roles...")
            try:
                results['roles_setup'] = seed_roles(session)
                if results['roles_setup']:
                    logger.info("Roles setup completed")
                else:
                    logger.error("Roles setup failed")
                    results['errors'].append("Failed to setup roles")
            except Exception as e:
                logger.error(f"Error in roles setup: {e}")
                results['errors'].append(f"Roles setup error: {e}")

            # Step 2: Fix any existing constraint issues
            logger.info("Step 2: Fixing constraint issues...")
            try:
                fix_results = self.constraint_fixer.full_fix()
                results['constraints_fixed'] = fix_results.get('success', False)
                if results['constraints_fixed']:
                    logger.info("Constraints fixed")
                else:
                    logger.error("Constraint fixing failed")
                    results['errors'].append("Failed to fix constraints")
            except Exception as e:
                logger.error(f"Error fixing constraints: {e}")
                results['errors'].append(f"Constraint fix error: {e}")

            # Step 3: Setup admin user
            logger.info("Step 3: Setting up admin user...")
            try:
                results['admin_setup'] = seed_default_admin(self.user_repository)
                if results['admin_setup']:
                    logger.info("Admin user setup completed")
                else:
                    logger.error("Admin user setup failed")
                    results['errors'].append("Failed to setup admin user")
            except Exception as e:
                logger.error(f"Error in admin setup: {e}")
                results['errors'].append(f"Admin setup error: {e}")

            # Step 4: Final verification
            logger.info("Step 4: Final verification...")
            try:
                verification = self.verify_database_integrity()
                results['verification_passed'] = verification['success']
                if results['verification_passed']:
                    logger.info("Database verification passed")
                else:
                    logger.error("Database verification failed")
                    results['errors'].extend(verification.get('errors', []))
            except Exception as e:
                logger.error(f"Error in verification: {e}")
                results['errors'].append(f"Verification error: {e}")

            # Overall success
            results['success'] = (
                results['roles_setup'] and
                results['constraints_fixed'] and
                results['admin_setup'] and
                results['verification_passed']
            )

            if results['success']:
                logger.info("Database setup completed successfully!")
            else:
                logger.error("Database setup completed with errors")
            
            return results
            
        except Exception as e:
            logger.error(f"Critical error in database setup: {e}")
            return {
                'success': False,
                'errors': [f"Critical setup error: {e}"]
            }
    
    def verify_database_integrity(self) -> Dict[str, Any]:
        """
        Verify complete database integrity
        
        Returns:
            dict: Verification results
        """
        try:
            logger.info("Verifying database integrity...")

            results = {
                'role_integrity': {},
                'constraint_integrity': False,
                'admin_exists': False,
                'success': False,
                'errors': []
            }

            # Check role integrity
            results['role_integrity'] = verify_roles(session)
            if not results['role_integrity'].get('integrity_ok', False):
                results['errors'].append("Role integrity check failed")

            # Check constraint integrity
            results['constraint_integrity'] = self.constraint_fixer.verify_foreign_key_constraints()
            if not results['constraint_integrity']:
                results['errors'].append("Foreign key constraint violations found")

            # Check admin exists
            admin_user = self.user_repository.get_by_email('thienphuc12a1ltt@gmail.com')
            results['admin_exists'] = admin_user is not None
            if not results['admin_exists']:
                results['errors'].append("Admin user not found")
            
            # Overall success
            results['success'] = (
                results['role_integrity'].get('integrity_ok', False) and
                results['constraint_integrity'] and
                results['admin_exists']
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Error verifying database integrity: {e}")
            return {
                'success': False,
                'errors': [f"Verification error: {e}"]
            }
    
    def print_setup_summary(self, results: Dict[str, Any]):
        """
        Print setup summary to console
        
        Args:
            results: Setup results dictionary
        """
        print("\n" + "="*60)
        print("DATABASE SETUP SUMMARY")
        print("="*60)

        # Status indicators
        status_text = "SUCCESS" if results['success'] else "FAILED"
        print(f"\nOverall Status: {status_text}")

        # Individual components
        print(f"\nComponents:")
        print(f"  [{'OK' if results.get('roles_setup') else 'FAIL'}] Roles Setup")
        print(f"  [{'OK' if results.get('constraints_fixed') else 'FAIL'}] Constraints Fixed")
        print(f"  [{'OK' if results.get('admin_setup') else 'FAIL'}] Admin User Setup")
        print(f"  [{'OK' if results.get('verification_passed') else 'FAIL'}] Verification Passed")

        # Errors
        if results.get('errors'):
            print(f"\nErrors ({len(results['errors'])}):")
            for error in results['errors']:
                print(f"  - {error}")

        # Next steps
        if results['success']:
            print(f"\nDatabase is ready to use!")
            print(f"   - Admin email: thienphuc12a1ltt@gmail.com")
            print(f"   - Admin password: admin123")
            print(f"   - Default user role ID: 2")
            print(f"   - Admin role ID: 1")
        else:
            print(f"\nNext steps:")
            print(f"   - Review error messages above")
            print(f"   - Run individual fix scripts if needed")
            print(f"   - Check database connection and permissions")
        
        print("="*60)

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
        print("TicketResell Database Setup")
        print("This script will setup roles, fix constraints, and create admin user")

        # Ask for confirmation
        response = input("\nDo you want to proceed? (y/N): ").strip().lower()

        if response not in ['y', 'yes']:
            print("Setup cancelled by user")
            sys.exit(0)

        # Run setup
        setup = DatabaseSetup()
        results = setup.setup_complete_database()

        # Print summary
        setup.print_setup_summary(results)

        # Exit with appropriate code
        sys.exit(0 if results['success'] else 1)

    except KeyboardInterrupt:
        print("\nSetup interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Critical error: {e}")
        print(f"\nCritical error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
