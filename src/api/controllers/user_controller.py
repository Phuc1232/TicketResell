from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from services.user_service import UserService
from infrastructure.repositories.user_repository import UserRepository
from api.schemas.user import UserRegisterSchema, UserLoginSchema, UserResponseSchema, UserUpdateSchema, UserVerificationSchema, UserRatingSchema
from infrastructure.databases.mssql import session

bp = Blueprint('user', __name__, url_prefix='/users')
user_service = UserService(UserRepository(session))

register_schema = UserRegisterSchema()
login_schema = UserLoginSchema()
response_schema = UserResponseSchema()
update_schema = UserUpdateSchema()
verification_schema = UserVerificationSchema()
rating_schema = UserRatingSchema()

def is_admin(user_id: int) -> bool:
    """Kiểm tra user có phải admin không"""
    user = user_service.get_user(user_id)
    return user and user.role_id == 1  # Giả sử role_id = 1 là admin

def can_delete_user(current_user_id: int, target_user_id: int) -> bool:
    """Kiểm tra quyền xóa user: admin hoặc chính user đó"""
    return current_user_id == target_user_id or is_admin(current_user_id)

@bp.route('/', methods=['GET'])
@jwt_required()
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
    current_user_id = int(get_jwt_identity())
    if not is_admin(current_user_id):
        return jsonify({"message": "Access denied - Admin only"}), 403
    
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

@bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    ---
    post:
      summary: Register a new user
      tags:
        - Users
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UserRegister'
      responses:
        201:
          description: User created successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserResponse'
    """
    data = request.get_json()
    errors = register_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    user = user_service.register_user(**data)
    return jsonify(response_schema.dump(user)), 201

@bp.route('/login', methods=['POST'])
def login():
    """
    Login and get JWT token
    ---
    post:
      summary: Login
      tags:
        - Users
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UserLogin'
      responses:
        200:
          description: JWT token
    """
    data = request.get_json()
    errors = login_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    user = user_service.authenticate_user(data['email'], data['password'])
    if not user:
        return jsonify({"message": "Invalid credentials"}), 401
    token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": token}), 200

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
    user_id = int(get_jwt_identity())
    user = user_service.get_user(user_id)
    return jsonify(response_schema.dump(user)), 200

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
        user_id = int(get_jwt_identity())
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
        user_id = int(get_jwt_identity())
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
        current_user_id = int(get_jwt_identity())
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
def delete_user(user_id):
    """
    Delete a user by ID (Admin or self only)
    ---
    delete:
      summary: Delete a user by ID
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
          description: Access denied - Can only delete yourself or admin only
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
    current_user_id = int(get_jwt_identity())
    
    # Kiểm tra quyền xóa
    if not can_delete_user(current_user_id, user_id):
        return jsonify({"message": "Access denied - Can only delete yourself or admin only"}), 403
    
    try:
        user_service.delete_user(user_id)
        return '', 204
    except ValueError as e:
        return jsonify({"message": str(e)}), 404
