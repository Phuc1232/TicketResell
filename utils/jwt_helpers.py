"""
JWT Helper Functions for Role-Based Authentication
"""

from flask_jwt_extended import get_jwt_identity, get_jwt
from typing import Dict, Any, Optional
import json


def create_jwt_identity(user_id: int, role_id: int, username: str = None) -> str:
    """
    Create JWT identity payload with user info and role
    
    Args:
        user_id: User ID
        role_id: User role ID (1=Admin, 2=User)
        username: Optional username for debugging
        
    Returns:
        JSON string containing user identity
    """
    identity_data = {
        "user_id": user_id,
        "role_id": role_id
    }
    
    if username:
        identity_data["username"] = username
        
    return json.dumps(identity_data)


def get_current_user_id() -> int:
    """
    Get current user ID from JWT token
    
    Returns:
        User ID as integer
        
    Raises:
        ValueError: If token is invalid or missing
    """
    try:
        identity = get_jwt_identity()
        
        # Handle both old format (string) and new format (JSON)
        if isinstance(identity, str):
            try:
                # Try to parse as JSON (new format)
                identity_data = json.loads(identity)
                return int(identity_data["user_id"])
            except (json.JSONDecodeError, KeyError):
                # Fallback to old format (just user_id as string)
                return int(identity)
        
        return int(identity)
        
    except Exception as e:
        raise ValueError(f"Invalid JWT token: {e}")


def get_current_user_role() -> int:
    """
    Get current user role ID from JWT token
    
    Returns:
        Role ID (1=Admin, 2=User)
        
    Raises:
        ValueError: If token is invalid or role not found
    """
    try:
        identity = get_jwt_identity()
        
        if isinstance(identity, str):
            try:
                # Parse JSON format
                identity_data = json.loads(identity)
                return int(identity_data["role_id"])
            except (json.JSONDecodeError, KeyError):
                # Old format doesn't have role - assume regular user
                return 2  # Default to regular user
        
        return 2  # Default fallback
        
    except Exception as e:
        raise ValueError(f"Invalid JWT token: {e}")


def get_current_user_info() -> Dict[str, Any]:
    """
    Get complete current user info from JWT token
    
    Returns:
        Dict with user_id, role_id, and optional username
        
    Raises:
        ValueError: If token is invalid
    """
    try:
        identity = get_jwt_identity()
        
        if isinstance(identity, str):
            try:
                # Parse JSON format
                identity_data = json.loads(identity)
                return {
                    "user_id": int(identity_data["user_id"]),
                    "role_id": int(identity_data["role_id"]),
                    "username": identity_data.get("username"),
                    "is_admin": int(identity_data["role_id"]) == 1
                }
            except (json.JSONDecodeError, KeyError):
                # Fallback to old format
                return {
                    "user_id": int(identity),
                    "role_id": 2,  # Default to regular user
                    "username": None,
                    "is_admin": False
                }
        
        # Fallback
        return {
            "user_id": int(identity),
            "role_id": 2,
            "username": None,
            "is_admin": False
        }
        
    except Exception as e:
        raise ValueError(f"Invalid JWT token: {e}")


def is_admin() -> bool:
    """
    Check if current user is admin
    
    Returns:
        True if user is admin (role_id = 1), False otherwise
    """
    try:
        role_id = get_current_user_role()
        return role_id == 1
    except:
        return False


def is_user_or_admin(target_user_id: int) -> bool:
    """
    Check if current user can access target user's data
    (either the user themselves or an admin)
    
    Args:
        target_user_id: ID of the target user
        
    Returns:
        True if access allowed, False otherwise
    """
    try:
        current_user_id = get_current_user_id()
        current_role = get_current_user_role()
        
        # Admin can access anyone
        if current_role == 1:
            return True
            
        # User can access their own data
        return current_user_id == target_user_id
        
    except:
        return False


def get_jwt_claims() -> Dict[str, Any]:
    """
    Get additional JWT claims if any
    
    Returns:
        Dict with JWT claims
    """
    try:
        return get_jwt()
    except:
        return {}


# Role constants for better code readability
class Roles:
    ADMIN = 1
    USER = 2
    
    @classmethod
    def is_valid_role(cls, role_id: int) -> bool:
        """Check if role_id is valid"""
        return role_id in [cls.ADMIN, cls.USER]
    
    @classmethod
    def get_role_name(cls, role_id: int) -> str:
        """Get human-readable role name"""
        role_names = {
            cls.ADMIN: "Admin",
            cls.USER: "User"
        }
        return role_names.get(role_id, "Unknown")
