"""
Admin Service - Handles admin-specific operations and system management
"""

from typing import List, Dict, Any, Optional
from domain.models.user import User
from domain.models.iuser_repository import IUserRepository
from services.user_service import UserService
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class AdminService:
    """
    Admin Service - Handles administrative operations
    Provides high-level admin functions with proper logging and validation
    """

    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository
        self.user_service = UserService(user_repository)

    def get_system_stats(self) -> Dict[str, Any]:
        """
        Get system statistics for admin dashboard
        
        Returns:
            Dict with system statistics
        """
        try:
            users = self.user_repository.list()
            
            # Basic user statistics
            total_users = len(users)
            verified_users = len([u for u in users if u.verified])
            admin_users = len([u for u in users if u.role_id == 1])
            active_users = len([u for u in users if u.status == 'active'])
            
            # Calculate percentages
            verification_rate = (verified_users / total_users * 100) if total_users > 0 else 0
            admin_percentage = (admin_users / total_users * 100) if total_users > 0 else 0
            
            stats = {
                "users": {
                    "total": total_users,
                    "verified": verified_users,
                    "unverified": total_users - verified_users,
                    "admins": admin_users,
                    "regular_users": total_users - admin_users,
                    "active": active_users,
                    "inactive": total_users - active_users,
                    "verification_rate": round(verification_rate, 2),
                    "admin_percentage": round(admin_percentage, 2)
                },
                "system": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "version": "1.0.0"
                }
            }
            
            logger.info(f"System stats generated: {total_users} total users, {verified_users} verified")
            return stats
            
        except Exception as e:
            logger.error(f"Error generating system stats: {e}")
            raise ValueError(f"Failed to generate system statistics: {e}")

    def get_all_users_detailed(self) -> List[Dict[str, Any]]:
        """
        Get all users with detailed information for admin view
        
        Returns:
            List of user dictionaries with detailed info
        """
        try:
            users = self.user_repository.list()
            
            detailed_users = []
            for user in users:
                user_info = {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "phone_number": user.phone_number,
                    "status": user.status,
                    "verified": user.verified,
                    "role_id": user.role_id,
                    "role_name": "Admin" if user.role_id == 1 else "User",
                    "create_date": user.create_date.isoformat() if user.create_date else None,
                    "date_of_birth": user.date_of_birth.isoformat() if user.date_of_birth else None,
                    "has_verification_pending": bool(user.verification_code),
                    "verification_expires_at": user.verification_expires_at.isoformat() if user.verification_expires_at else None
                }
                detailed_users.append(user_info)
            
            # Sort by creation date (newest first)
            detailed_users.sort(key=lambda x: x['create_date'] or '', reverse=True)
            
            logger.info(f"Retrieved detailed info for {len(detailed_users)} users")
            return detailed_users
            
        except Exception as e:
            logger.error(f"Error retrieving detailed user list: {e}")
            raise ValueError(f"Failed to retrieve user list: {e}")

    def force_delete_user(self, admin_user_id: int, target_user_id: int, reason: str = None) -> bool:
        """
        Force delete a user (admin only operation)
        
        Args:
            admin_user_id: ID of the admin performing the action
            target_user_id: ID of the user to delete
            reason: Optional reason for deletion
            
        Returns:
            True if successful
            
        Raises:
            ValueError: If operation fails or user not found
        """
        try:
            # Get admin user for logging
            admin_user = self.user_repository.get_by_id(admin_user_id)
            if not admin_user or admin_user.role_id != 1:
                raise ValueError("Only admins can perform force delete operations")
            
            # Get target user
            target_user = self.user_repository.get_by_id(target_user_id)
            if not target_user:
                raise ValueError(f"User with ID {target_user_id} not found")
            
            # Prevent admin from deleting themselves
            if admin_user_id == target_user_id:
                raise ValueError("Admins cannot delete their own account")
            
            # Log the deletion attempt
            log_message = f"Admin {admin_user.username} (ID: {admin_user_id}) deleting user {target_user.username} (ID: {target_user_id})"
            if reason:
                log_message += f" - Reason: {reason}"
            logger.warning(log_message)
            
            # Perform hard deletion (cascade delete related data)
            self.user_repository.delete(target_user_id)
            logger.info(f"User {target_user_id} successfully HARD DELETED by admin {admin_user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error in force delete user: {e}")
            raise ValueError(f"Failed to delete user: {e}")

    def update_user_status(self, admin_user_id: int, target_user_id: int, new_status: str, reason: str = None) -> User:
        """
        Update user status (admin only operation)
        
        Args:
            admin_user_id: ID of the admin performing the action
            target_user_id: ID of the user to update
            new_status: New status ('active', 'inactive', 'suspended')
            reason: Optional reason for status change
            
        Returns:
            Updated user object
            
        Raises:
            ValueError: If operation fails or invalid status
        """
        valid_statuses = ['active', 'inactive', 'suspended']
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        try:
            # Get admin user for logging
            admin_user = self.user_repository.get_by_id(admin_user_id)
            if not admin_user or admin_user.role_id != 1:
                raise ValueError("Only admins can update user status")
            
            # Get target user
            target_user = self.user_repository.get_by_id(target_user_id)
            if not target_user:
                raise ValueError(f"User with ID {target_user_id} not found")
            
            old_status = target_user.status
            
            # Update status
            target_user.status = new_status
            updated_user = self.user_repository.update(target_user)
            
            # Log the status change
            log_message = f"Admin {admin_user.username} (ID: {admin_user_id}) changed user {target_user.username} (ID: {target_user_id}) status from '{old_status}' to '{new_status}'"
            if reason:
                log_message += f" - Reason: {reason}"
            logger.info(log_message)
            
            return updated_user
            
        except Exception as e:
            logger.error(f"Error updating user status: {e}")
            raise ValueError(f"Failed to update user status: {e}")

    def search_users_advanced(self, query: str = '', filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Advanced user search for admin interface
        
        Args:
            query: Search query (username, email)
            filters: Additional filters (status, role_id, verified, etc.)
            
        Returns:
            List of matching users with detailed info
        """
        try:
            users = self.user_repository.list()
            filtered_users = []
            
            for user in users:
                # Text search
                if query:
                    query_lower = query.lower()
                    if not (query_lower in user.username.lower() or 
                           query_lower in user.email.lower()):
                        continue
                
                # Apply filters
                if filters:
                    if 'status' in filters and user.status != filters['status']:
                        continue
                    if 'role_id' in filters and user.role_id != filters['role_id']:
                        continue
                    if 'verified' in filters and user.verified != filters['verified']:
                        continue
                
                # Add to results
                user_info = {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "status": user.status,
                    "verified": user.verified,
                    "role_id": user.role_id,
                    "role_name": "Admin" if user.role_id == 1 else "User",
                    "create_date": user.create_date.isoformat() if user.create_date else None
                }
                filtered_users.append(user_info)
            
            logger.info(f"Advanced search returned {len(filtered_users)} users for query: '{query}'")
            return filtered_users
            
        except Exception as e:
            logger.error(f"Error in advanced user search: {e}")
            raise ValueError(f"Search failed: {e}")

    def get_recent_registrations(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get recent user registrations for admin monitoring
        
        Args:
            days: Number of days to look back (default: 7)
            
        Returns:
            List of recent registrations
        """
        try:
            users = self.user_repository.list()
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            recent_users = []
            for user in users:
                if user.create_date and user.create_date >= cutoff_date:
                    user_info = {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "verified": user.verified,
                        "create_date": user.create_date.isoformat(),
                        "days_ago": (datetime.utcnow() - user.create_date).days
                    }
                    recent_users.append(user_info)
            
            # Sort by creation date (newest first)
            recent_users.sort(key=lambda x: x['create_date'], reverse=True)
            
            logger.info(f"Found {len(recent_users)} registrations in the last {days} days")
            return recent_users
            
        except Exception as e:
            logger.error(f"Error retrieving recent registrations: {e}")
            raise ValueError(f"Failed to retrieve recent registrations: {e}")
