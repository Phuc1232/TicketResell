from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.user_service import UserService
from infrastructure.repositories.user_repository import UserRepository
from api.schemas.user import UserResponseSchema, UserUpdateSchema, UserRatingSchema, UserVerificationSchema
from infrastructure.databases.mssql import session
from api.decorators.auth_decorators import admin_required, owner_or_admin_required, delete_permission_required
from utils.jwt_helpers import get_current_user_id, get_current_user_role

bp = Blueprint('user', __name__, url_prefix='/users')
user_service = UserService(UserRepository(session))

# Only schemas needed for user management (auth schemas moved to auth_controller)
response_schema = UserResponseSchema()
update_schema = UserUpdateSchema()
rating_schema = UserRatingSchema()
verification_schema = UserVerificationSchema()

# Legacy functions - now replaced by decorators and JWT helpers
# Keeping for backward compatibility, but deprecated
def is_admin(user_id: int) -> bool:
    """DEPRECATED: Use utils.jwt_helpers.is_admin() instead"""
    user = user_service.get_user(user_id)
    return user and user.role_id == 1

def can_delete_user(current_user_id: int, target_user_id: int) -> bool:
    """DEPRECATED: Use decorators instead"""
    return current_user_id == target_user_id or is_admin(current_user_id)

@bp.route('/', methods=['GET'])
@jwt_required()
@admin_required
def list_users():
    """
    Get all users (Admin only)
    ---
    get:
      summary: Get all users
      security:
        - BearerAuth: []
      tags:
        - Users
      responses:
        200:
          description: List of users
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/UserResponse'
        403:
          description: Access denied - Admin only
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
    """
    users = user_service.list_users()
    return jsonify(response_schema.dump(users, many=True)), 200

@bp.route('/search', methods=['GET'])
def search_users():
    """
    Search users by criteria
    ---
    get:
      summary: Search users by criteria
      parameters:
        - name: q
          in: query
          schema:
            type: string
          description: Search query (username, email)
        - name: verified
          in: query
          schema:
            type: boolean
          description: Filter by verification status
        - name: min_rating
          in: query
          schema:
            type: number
          description: Minimum rating
        - name: status
          in: query
          schema:
            type: string
          description: User status filter
      tags:
        - Users
      responses:
        200:
          description: List of matching users
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/UserResponse'
    """
    try:
        query = request.args.get('q', '')
        verified = request.args.get('verified')
        min_rating = request.args.get('min_rating')
        status = request.args.get('status')
        
        users = user_service.search_users(query, verified, min_rating, status)
        return jsonify(response_schema.dump(users, many=True)), 200
    except Exception as e:
        return jsonify({"message": "Error searching users", "error": str(e)}), 500

# Authentication endpoints moved to /api/auth/
# This controller now focuses only on user profile management

@bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    """
    Get current user info
    ---
    get:
      summary: Get current user
      security:
        - BearerAuth: []
      tags:
        - Users
      responses:
        200:
          description: User info
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserResponse'
    """
    user_id = get_current_user_id()
    user = user_service.get_user(user_id)
    return jsonify(response_schema.dump(user)), 200

# Internal endpoint - keep ID-based
@bp.route('/internal/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    """
    Get user by ID (Internal use)
    ---
    get:
      summary: Get user by ID (Internal use)
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: integer
          description: ID of the user to get
      tags:
        - Users
      responses:
        200:
          description: User info
        404:
          description: User not found
    """
    user = user_service.get_user(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    return jsonify(response_schema.dump(user)), 200

# Public endpoint - use username
@bp.route('/profile/<username>', methods=['GET'])
def get_user_profile(username):
    """
    Get user profile by username (Public)
    ---
    get:
      summary: Get user profile by username
      parameters:
        - name: username
          in: path
          required: true
          schema:
            type: string
          description: Username of the user
      tags:
        - Users
      responses:
        200:
          description: User profile
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserResponse'
        404:
          description: User not found
    """
    user = user_service.get_user_by_username(username)
    if not user:
        return jsonify({"message": "User not found"}), 404
    return jsonify(response_schema.dump(user)), 200

@bp.route('/<username>/tickets', methods=['GET'])
def get_user_tickets(username):
    """
    Get tickets owned by user (Public)
    ---
    get:
      summary: Get tickets owned by user
      parameters:
        - name: username
          in: path
          required: true
          schema:
            type: string
          description: Username of the ticket owner
      tags:
        - Users
      responses:
        200:
          description: List of user's tickets
        404:
          description: User not found
    """
    user = user_service.get_user_by_username(username)
    if not user:
        return jsonify({"message": "User not found"}), 404

    # Get tickets owned by this user
    from services.ticket_service import TicketService
    from infrastructure.repositories.ticket_repository import TicketRepository
    from infrastructure.databases.mssql import session

    ticket_service = TicketService(TicketRepository(session))
    tickets = ticket_service.get_tickets_by_owner(user.id)

    from api.schemas.ticket import TicketResponseSchema
    ticket_schema = TicketResponseSchema(many=True)

    return jsonify({
        "user": {
            "username": user.username,
            "id": user.id
        },
        "tickets": ticket_schema.dump(tickets),
        "total_tickets": len(tickets)
    }), 200

@bp.route('/me', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    Update current user profile
    ---
    put:
      summary: Update current user profile
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UserUpdate'
      tags:
        - Users
      responses:
        200:
          description: Profile updated successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserResponse'
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        errors = update_schema.validate(data)
        if errors:
            return jsonify({"message": "Validation errors", "errors": errors}), 400
        
        user = user_service.update_profile(user_id, **data)
        return jsonify(response_schema.dump(user)), 200
    except Exception as e:
        return jsonify({"message": "Error updating profile", "error": str(e)}), 500

@bp.route('/verify', methods=['POST'])
@jwt_required()
def verify_user():
    """
    Verify user account
    ---
    post:
      summary: Verify user account
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UserVerification'
      tags:
        - Users
      responses:
        200:
          description: User verified successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserResponse'
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()

        errors = verification_schema.validate(data)
        if errors:
            return jsonify({"message": "Validation errors", "errors": errors}), 400

        user = user_service.verify_user(user_id, data['verification_code'], data['verification_type'])
        return jsonify(response_schema.dump(user)), 200
    except Exception as e:
        return jsonify({"message": "Error verifying user", "error": str(e)}), 500

@bp.route('/<int:target_user_id>/rate', methods=['POST'])
@jwt_required()
def rate_user(target_user_id):
    """
    Rate another user
    ---
    post:
      summary: Rate another user
      security:
        - BearerAuth: []
      parameters:
        - name: target_user_id
          in: path
          required: true
          schema:
            type: integer
          description: ID of the user to rate
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UserRating'
      tags:
        - Users
      responses:
        200:
          description: User rated successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserResponse'
    """
    try:
        current_user_id = get_current_user_id()
        data = request.get_json()
        
        errors = rating_schema.validate(data)
        if errors:
            return jsonify({"message": "Validation errors", "errors": errors}), 400
        
        # Không cho phép tự rate chính mình
        if current_user_id == target_user_id:
            return jsonify({"message": "Cannot rate yourself"}), 400
        
        user = user_service.rate_user(current_user_id, target_user_id, data['rating'], 
                                     data.get('comment'), data['transaction_id'])
        return jsonify(response_schema.dump(user)), 200
    except Exception as e:
        return jsonify({"message": "Error rating user", "error": str(e)}), 500

@bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
@delete_permission_required
def delete_user(user_id):
    """
    Delete a user by ID (Admin only)
    ---
    delete:
      summary: Delete a user by ID (Admin only)
      security:
        - BearerAuth: []
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: integer
          description: ID of the user to delete
      tags:
        - Users
      responses:
        204:
          description: User deleted successfully
        403:
          description: Access denied - Admin privileges required
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
        404:
          description: User not found
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
    """
    try:
        user_service.delete_user(user_id)
        return '', 204
    except ValueError as e:
        return jsonify({"message": str(e)}), 404
