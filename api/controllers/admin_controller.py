"""
Admin Controller - Admin-only endpoints for system management
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from services.admin_service import AdminService
from infrastructure.repositories.user_repository import UserRepository
from infrastructure.databases.mssql import session
from api.decorators.auth_decorators import admin_required, delete_permission_required
from utils.jwt_helpers import get_current_user_id, get_current_user_info
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# Initialize admin service
admin_service = AdminService(UserRepository(session))


@bp.route('/stats', methods=['GET'])
@jwt_required()
@admin_required
def get_system_stats():
    """
    Get system statistics (Admin only)
    ---
    get:
      summary: Get system statistics and metrics
      security:
        - BearerAuth: []
      tags:
        - Admin
      responses:
        200:
          description: System statistics
          content:
            application/json:
              schema:
                type: object
                properties:
                  users:
                    type: object
                    properties:
                      total:
                        type: integer
                      verified:
                        type: integer
                      unverified:
                        type: integer
                      admins:
                        type: integer
                      regular_users:
                        type: integer
                      verification_rate:
                        type: number
                  system:
                    type: object
                    properties:
                      generated_at:
                        type: string
                      version:
                        type: string
        403:
          description: Access denied - Admin only
    """
    try:
        stats = admin_service.get_system_stats()
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        return jsonify({"message": "Error retrieving system statistics", "error": str(e)}), 500


@bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def get_all_users():
    """
    Get all users with detailed information (Admin only)
    ---
    get:
      summary: Get all users with detailed admin information
      security:
        - BearerAuth: []
      tags:
        - Admin
      responses:
        200:
          description: List of all users with detailed information
          content:
            application/json:
              schema:
                type: array
                items:
                  type: object
                  properties:
                    id:
                      type: integer
                    username:
                      type: string
                    email:
                      type: string
                    status:
                      type: string
                    verified:
                      type: boolean
                    role_id:
                      type: integer
                    role_name:
                      type: string
                    create_date:
                      type: string
        403:
          description: Access denied - Admin only
    """
    try:
        users = admin_service.get_all_users_detailed()
        return jsonify(users), 200
    except Exception as e:
        logger.error(f"Error getting all users: {e}")
        return jsonify({"message": "Error retrieving users", "error": str(e)}), 500


@bp.route('/users/search', methods=['GET'])
@jwt_required()
@admin_required
def search_users():
    """
    Advanced user search (Admin only)
    ---
    get:
      summary: Search users with advanced filters
      security:
        - BearerAuth: []
      parameters:
        - name: q
          in: query
          schema:
            type: string
          description: Search query (username, email)
        - name: status
          in: query
          schema:
            type: string
            enum: [active, inactive, suspended]
          description: Filter by user status
        - name: role_id
          in: query
          schema:
            type: integer
            enum: [1, 2]
          description: Filter by role (1=Admin, 2=User)
        - name: verified
          in: query
          schema:
            type: boolean
          description: Filter by verification status
      tags:
        - Admin
      responses:
        200:
          description: Search results
        403:
          description: Access denied - Admin only
    """
    try:
        query = request.args.get('q', '')
        
        # Build filters
        filters = {}
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        if request.args.get('role_id'):
            filters['role_id'] = int(request.args.get('role_id'))
        if request.args.get('verified') is not None:
            filters['verified'] = request.args.get('verified').lower() == 'true'
        
        users = admin_service.search_users_advanced(query, filters)
        return jsonify(users), 200
    except Exception as e:
        logger.error(f"Error in admin user search: {e}")
        return jsonify({"message": "Search failed", "error": str(e)}), 500


@bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
@delete_permission_required
def force_delete_user(user_id):
    """
    Force delete a user by ID (Admin only)
    ---
    delete:
      summary: Force delete any user by ID (Admin only)
      security:
        - BearerAuth: []
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: integer
          description: ID of the user to delete
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                reason:
                  type: string
                  description: Optional reason for deletion
      tags:
        - Admin
      responses:
        204:
          description: User deleted successfully
        403:
          description: Access denied - Admin only
        404:
          description: User not found
        400:
          description: Cannot delete own account
    """
    try:
        admin_user_id = get_current_user_id()
        data = request.get_json() or {}
        reason = data.get('reason')

        admin_service.force_delete_user(admin_user_id, user_id, reason)
        return '', 204
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg:
            return jsonify({"message": error_msg}), 404
        elif "cannot delete" in error_msg.lower():
            return jsonify({"message": error_msg}), 400
        else:
            return jsonify({"message": error_msg}), 400
    except Exception as e:
        logger.error(f"Error in force delete user: {e}")
        return jsonify({"message": "Error deleting user", "error": str(e)}), 500


@bp.route('/users/<int:user_id>/status', methods=['PUT'])
@jwt_required()
@admin_required
def update_user_status(user_id):
    """
    Update user status (Admin only)
    ---
    put:
      summary: Update user status (active/inactive/suspended)
      security:
        - BearerAuth: []
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: integer
          description: ID of the user to update
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
                  enum: [active, inactive, suspended]
                  description: New user status
                reason:
                  type: string
                  description: Optional reason for status change
              required:
                - status
      tags:
        - Admin
      responses:
        200:
          description: User status updated successfully
        400:
          description: Invalid status or validation error
        403:
          description: Access denied - Admin only
        404:
          description: User not found
    """
    try:
        admin_user_id = get_current_user_id()
        data = request.get_json()
        
        if not data or 'status' not in data:
            return jsonify({"message": "Status is required"}), 400
        
        new_status = data['status']
        reason = data.get('reason')
        
        updated_user = admin_service.update_user_status(admin_user_id, user_id, new_status, reason)
        
        return jsonify({
            "message": "User status updated successfully",
            "user": {
                "id": updated_user.id,
                "username": updated_user.username,
                "email": updated_user.email,
                "status": updated_user.status
            }
        }), 200
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg:
            return jsonify({"message": error_msg}), 404
        else:
            return jsonify({"message": error_msg}), 400
    except Exception as e:
        logger.error(f"Error updating user status: {e}")
        return jsonify({"message": "Error updating user status", "error": str(e)}), 500


@bp.route('/users/recent', methods=['GET'])
@jwt_required()
@admin_required
def get_recent_registrations():
    """
    Get recent user registrations (Admin only)
    ---
    get:
      summary: Get recent user registrations for monitoring
      security:
        - BearerAuth: []
      parameters:
        - name: days
          in: query
          schema:
            type: integer
            default: 7
          description: Number of days to look back
      tags:
        - Admin
      responses:
        200:
          description: List of recent registrations
        403:
          description: Access denied - Admin only
    """
    try:
        days = int(request.args.get('days', 7))
        if days < 1 or days > 365:
            return jsonify({"message": "Days must be between 1 and 365"}), 400
        
        recent_users = admin_service.get_recent_registrations(days)
        return jsonify({
            "recent_registrations": recent_users,
            "period_days": days,
            "total_count": len(recent_users)
        }), 200
    except Exception as e:
        logger.error(f"Error getting recent registrations: {e}")
        return jsonify({"message": "Error retrieving recent registrations", "error": str(e)}), 500


@bp.route('/me', methods=['GET'])
@jwt_required()
@admin_required
def get_admin_info():
    """
    Get current admin user information
    ---
    get:
      summary: Get current admin user details
      security:
        - BearerAuth: []
      tags:
        - Admin
      responses:
        200:
          description: Admin user information
        403:
          description: Access denied - Admin only
    """
    try:
        user_info = get_current_user_info()
        return jsonify({
            "admin_info": user_info,
            "permissions": [
                "view_all_users",
                "delete_users", 
                "update_user_status",
                "view_system_stats",
                "advanced_search"
            ]
        }), 200
    except Exception as e:
        logger.error(f"Error getting admin info: {e}")
        return jsonify({"message": "Error retrieving admin information", "error": str(e)}), 500
