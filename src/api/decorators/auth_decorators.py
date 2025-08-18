"""
Authorization Decorators for Role-Based Access Control
"""

from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.jwt_helpers import get_current_user_role, get_current_user_id, Roles
from typing import List, Callable, Any
import logging

logger = logging.getLogger(__name__)


def admin_required(f: Callable) -> Callable:
    """
    Decorator to require admin role (role_id = 1)
    
    Usage:
        @bp.route('/admin-only')
        @jwt_required()
        @admin_required
        def admin_endpoint():
            return "Admin only content"
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            role_id = get_current_user_role()
            
            if role_id != Roles.ADMIN:
                logger.warning(f"Non-admin user (role_id={role_id}) attempted to access admin endpoint: {f.__name__}")
                return jsonify({
                    "message": "Access denied - Admin privileges required",
                    "error_code": "INSUFFICIENT_PRIVILEGES",
                    "required_role": "Admin"
                }), 403
                
            return f(*args, **kwargs)
            
        except ValueError as e:
            logger.error(f"JWT validation error in admin_required: {e}")
            return jsonify({
                "message": "Invalid authentication token",
                "error_code": "INVALID_TOKEN"
            }), 401
        except Exception as e:
            logger.error(f"Unexpected error in admin_required: {e}")
            return jsonify({
                "message": "Authorization check failed",
                "error_code": "AUTH_ERROR"
            }), 500
            
    return decorated_function


def role_required(allowed_roles: List[int]) -> Callable:
    """
    Decorator to require specific roles
    
    Args:
        allowed_roles: List of allowed role IDs
        
    Usage:
        @bp.route('/admin-or-user')
        @jwt_required()
        @role_required([Roles.ADMIN, Roles.USER])
        def mixed_endpoint():
            return "Admin or User content"
            
        @bp.route('/admin-only')
        @jwt_required()
        @role_required([Roles.ADMIN])
        def admin_only():
            return "Admin only"
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                role_id = get_current_user_role()
                
                if role_id not in allowed_roles:
                    role_names = [Roles.get_role_name(r) for r in allowed_roles]
                    current_role_name = Roles.get_role_name(role_id)
                    
                    logger.warning(f"User with role '{current_role_name}' (role_id={role_id}) attempted to access endpoint requiring roles: {role_names}")
                    
                    return jsonify({
                        "message": f"Access denied - Required roles: {', '.join(role_names)}",
                        "error_code": "INSUFFICIENT_PRIVILEGES",
                        "current_role": current_role_name,
                        "required_roles": role_names
                    }), 403
                    
                return f(*args, **kwargs)
                
            except ValueError as e:
                logger.error(f"JWT validation error in role_required: {e}")
                return jsonify({
                    "message": "Invalid authentication token",
                    "error_code": "INVALID_TOKEN"
                }), 401
            except Exception as e:
                logger.error(f"Unexpected error in role_required: {e}")
                return jsonify({
                    "message": "Authorization check failed",
                    "error_code": "AUTH_ERROR"
                }), 500
                
        return decorated_function
    return decorator


def owner_or_admin_required(user_id_param: str = 'user_id') -> Callable:
    """
    Decorator to allow access only to resource owner or admin
    
    Args:
        user_id_param: Name of the parameter containing the target user ID
        
    Usage:
        @bp.route('/users/<int:user_id>/profile')
        @jwt_required()
        @owner_or_admin_required('user_id')
        def get_user_profile(user_id):
            return f"Profile for user {user_id}"
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                current_user_id = get_current_user_id()
                current_role = get_current_user_role()
                
                # Get target user ID from parameters
                target_user_id = kwargs.get(user_id_param)
                if target_user_id is None:
                    return jsonify({
                        "message": f"Missing required parameter: {user_id_param}",
                        "error_code": "MISSING_PARAMETER"
                    }), 400
                
                # Admin can access anything
                if current_role == Roles.ADMIN:
                    return f(*args, **kwargs)
                
                # User can only access their own resources
                if current_user_id == target_user_id:
                    return f(*args, **kwargs)
                
                logger.warning(f"User {current_user_id} attempted to access user {target_user_id}'s resource")
                return jsonify({
                    "message": "Access denied - You can only access your own resources or admin privileges required",
                    "error_code": "INSUFFICIENT_PRIVILEGES"
                }), 403
                
            except ValueError as e:
                logger.error(f"JWT validation error in owner_or_admin_required: {e}")
                return jsonify({
                    "message": "Invalid authentication token",
                    "error_code": "INVALID_TOKEN"
                }), 401
            except Exception as e:
                logger.error(f"Unexpected error in owner_or_admin_required: {e}")
                return jsonify({
                    "message": "Authorization check failed",
                    "error_code": "AUTH_ERROR"
                }), 500
                
        return decorated_function
    return decorator


def delete_permission_required(f: Callable) -> Callable:
    """
    Decorator specifically for delete operations - Admin only
    
    Usage:
        @bp.route('/users/<int:user_id>', methods=['DELETE'])
        @jwt_required()
        @delete_permission_required
        def delete_user(user_id):
            return "User deleted"
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            role_id = get_current_user_role()
            
            if role_id != Roles.ADMIN:
                current_role_name = Roles.get_role_name(role_id)
                logger.warning(f"User with role '{current_role_name}' attempted delete operation on endpoint: {f.__name__}")
                
                return jsonify({
                    "message": "Access denied - Delete operations require Admin privileges",
                    "error_code": "DELETE_PERMISSION_DENIED",
                    "current_role": current_role_name,
                    "required_role": "Admin"
                }), 403
                
            return f(*args, **kwargs)
            
        except ValueError as e:
            logger.error(f"JWT validation error in delete_permission_required: {e}")
            return jsonify({
                "message": "Invalid authentication token",
                "error_code": "INVALID_TOKEN"
            }), 401
        except Exception as e:
            logger.error(f"Unexpected error in delete_permission_required: {e}")
            return jsonify({
                "message": "Authorization check failed",
                "error_code": "AUTH_ERROR"
            }), 500
            
    return decorated_function


# Convenience decorators for common use cases
def admin_only(f: Callable) -> Callable:
    """Alias for admin_required - more readable"""
    return admin_required(f)


def authenticated_user(f: Callable) -> Callable:
    """Decorator for endpoints that require any authenticated user"""
    return role_required([Roles.ADMIN, Roles.USER])(f)
