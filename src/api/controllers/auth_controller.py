from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from utils.jwt_helpers import get_current_user_id
from services.auth_service import (
    AuthService,
    VerificationCodeExpiredError,
    VerificationCodeInvalidError,
    UserAlreadyVerifiedError
)
from services.email_service import EmailService
from infrastructure.repositories.user_repository import UserRepository
from infrastructure.databases.mssql import session
from api.schemas.auth_schemas import (
    register_schema, login_schema, verification_schema, change_password_schema,
    reset_password_schema, confirm_reset_schema, resend_verification_schema
)
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Initialize services
user_repository = UserRepository(session)
email_service = EmailService()
auth_service = AuthService(user_repository, email_service)

# Schemas are imported from auth_schemas.py

@bp.route('/register', methods=['POST'])
def register():
    """
    User registration
    ---
    post:
      summary: Register a new user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                username:
                  type: string
                  minLength: 3
                  maxLength: 50
                  description: Username (3-50 characters, alphanumeric and underscore only)
                email:
                  type: string
                  format: email
                  description: User email address
                password:
                  type: string
                  minLength: 6
                  description: Password (min 6 characters, must contain letter and number)
                phone_number:
                  type: string
                  minLength: 10
                  maxLength: 15
                  description: Phone number (10-15 digits)
                date_of_birth:
                  type: string
                  format: date-time
                  description: Date of birth (ISO format, e.g., 1990-01-15T00:00:00Z)
              required:
                - username
                - email
                - password
                - phone_number
                - date_of_birth
      tags:
        - Authentication
      responses:
        201:
          description: Registration successful
          content:
            application/json:
              schema:
                type: object
                properties:
                  user_id:
                    type: integer
                  email:
                    type: string
                  username:
                    type: string
                  verified:
                    type: boolean
                  temp_token:
                    type: string
                  message:
                    type: string
        400:
          description: Validation errors
        409:
          description: User already exists
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "No data provided"}), 400

        errors = register_schema.validate(data)
        if errors:
            return jsonify({"message": "Validation errors", "errors": errors}), 400

        # Use AuthService for registration
        result = auth_service.register_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            phone_number=data['phone_number'],
            date_of_birth=data['date_of_birth']
        )

        return jsonify(result), 201

    except ValueError as e:
        error_message = str(e)
        if "already exists" in error_message:
            return jsonify({"message": error_message}), 409
        return jsonify({"message": error_message}), 400
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({"message": "Error during registration", "error": str(e)}), 500

@bp.route('/login', methods=['POST'])
def login():
    """
    User login
    ---
    post:
      summary: User login
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                email:
                  type: string
                  format: email
                  description: User email
                password:
                  type: string
                  description: User password
              required:
                - email
                - password
      tags:
        - Authentication
      responses:
        200:
          description: Login successful
        401:
          description: Invalid credentials or account not verified
        400:
          description: Validation errors
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "No data provided"}), 400

        errors = login_schema.validate(data)
        if errors:
            return jsonify({"message": "Validation errors", "errors": errors}), 400

        # Use AuthService for authentication
        result = auth_service.authenticate_user(data['email'], data['password'])

        return jsonify({
            "access_token": result['access_token'],
            "refresh_token": result['refresh_token'],
            "token_type": result['token_type'],
            "user": {
                "id": result['user'].id,
                "username": result['user'].username,
                "email": result['user'].email,
                "verified": result['user'].verified,
                "role_id": result['user'].role_id,
                "is_admin": result['user'].role_id == 1
            },
            "message": result['message']
        }), 200

    except ValueError as e:
        error_message = str(e)
        if error_message == "ACCOUNT_NOT_VERIFIED":
            return jsonify({
                "message": "Account not verified",
                "error_code": "ACCOUNT_NOT_VERIFIED"
            }), 401
        return jsonify({"message": error_message}), 401
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({"message": "Error during login", "error": str(e)}), 500

@bp.route('/verify', methods=['POST'])
@jwt_required()
def verify_account():
    """
    Verify user account with verification code
    ---
    post:
      summary: Verify user account with 6-digit code
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                verification_code:
                  type: string
                  minLength: 6
                  maxLength: 6
                  description: 6-digit verification code
              required:
                - verification_code
      tags:
        - Authentication
      responses:
        200:
          description: Account verified successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  access_token:
                    type: string
                  refresh_token:
                    type: string
                  token_type:
                    type: string
                  user:
                    type: object
                  message:
                    type: string
        400:
          description: Invalid or expired verification code
        401:
          description: Unauthorized
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "No data provided"}), 400

        errors = verification_schema.validate(data)
        if errors:
            return jsonify({"message": "Validation errors", "errors": errors}), 400

        current_user_id = get_current_user_id()

        # Use AuthService for verification
        result = auth_service.verify_user(current_user_id, data['verification_code'])

        return jsonify({
            "access_token": result['access_token'],
            "refresh_token": result['refresh_token'],
            "token_type": result['token_type'],
            "user": {
                "id": result['user'].id,
                "username": result['user'].username,
                "email": result['user'].email,
                "verified": result['user'].verified,
                "role_id": result['user'].role_id,
                "is_admin": result['user'].role_id == 1
            },
            "message": result['message']
        }), 200

    except VerificationCodeExpiredError as e:
        return jsonify({
            "message": str(e),
            "error_code": "VERIFICATION_CODE_EXPIRED",
            "can_resend": True
        }), 400
    except VerificationCodeInvalidError as e:
        return jsonify({
            "message": str(e),
            "error_code": "VERIFICATION_CODE_INVALID",
            "can_resend": False
        }), 400
    except UserAlreadyVerifiedError as e:
        return jsonify({
            "message": str(e),
            "error_code": "USER_ALREADY_VERIFIED",
            "can_resend": False
        }), 400
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        logger.error(f"Verification error: {str(e)}")
        return jsonify({"message": "Error during verification", "error": str(e)}), 500

@bp.route('/resend-verification', methods=['POST'])
@jwt_required()
def resend_verification():
    """
    Resend verification code
    ---
    post:
      summary: Resend verification code to user email
      security:
        - BearerAuth: []
      tags:
        - Authentication
      responses:
        200:
          description: Verification code resent successfully
        400:
          description: User already verified or error sending email
        401:
          description: Unauthorized
    """
    try:
        current_user_id = get_current_user_id()

        # Use AuthService to resend verification code
        result = auth_service.resend_verification_code(current_user_id)

        return jsonify(result), 200

    except UserAlreadyVerifiedError as e:
        return jsonify({
            "message": str(e),
            "error_code": "USER_ALREADY_VERIFIED",
            "can_resend": False
        }), 400
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        logger.error(f"Resend verification error: {str(e)}")
        return jsonify({"message": "Error resending verification code", "error": str(e)}), 500

@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token using refresh token
    ---
    post:
      summary: Get new access token using refresh token
      security:
        - BearerAuth: []
      tags:
        - Authentication
      responses:
        200:
          description: New access token generated successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  access_token:
                    type: string
                    description: New access token (24h expiry)
                  token_type:
                    type: string
                    description: Token type (Bearer)
                  expires_in:
                    type: integer
                    description: Token expiry in seconds
                  user:
                    type: object
                    properties:
                      id:
                        type: integer
                      username:
                        type: string
                      role_id:
                        type: integer
                      is_admin:
                        type: boolean
                  message:
                    type: string
        401:
          description: Invalid or expired refresh token
        500:
          description: Server error
    """
    try:
        # Get user ID from refresh token
        current_user_id = get_jwt_identity()

        # Handle both old format (string) and new format (JSON)
        if isinstance(current_user_id, str):
            try:
                import json
                identity_data = json.loads(current_user_id)
                user_id_str = str(identity_data["user_id"])
            except (json.JSONDecodeError, KeyError):
                # Old format - just user_id as string
                user_id_str = current_user_id
        else:
            user_id_str = str(current_user_id)

        # Use AuthService to generate new access token
        result = auth_service.refresh_token(user_id_str)

        # Get user info for response
        from utils.jwt_helpers import get_current_user_info
        try:
            user_info = get_current_user_info()
        except:
            # Fallback if JWT helpers fail
            from infrastructure.repositories.user_repository import UserRepository
            user_repo = UserRepository(session)
            user = user_repo.get_by_id(int(user_id_str))
            user_info = {
                "user_id": user.id,
                "username": user.username,
                "role_id": user.role_id,
                "is_admin": user.role_id == 1
            } if user else {}

        return jsonify({
            "access_token": result['access_token'],
            "token_type": result['token_type'],
            "expires_in": 24 * 60 * 60,  # 24 hours in seconds
            "user": {
                "id": user_info.get("user_id"),
                "username": user_info.get("username"),
                "role_id": user_info.get("role_id"),
                "is_admin": user_info.get("is_admin", False)
            },
            "message": "Access token refreshed successfully"
        }), 200

    except ValueError as e:
        logger.warning(f"Token refresh failed: {e}")
        return jsonify({
            "message": str(e),
            "error_code": "REFRESH_TOKEN_INVALID"
        }), 401
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return jsonify({
            "message": "Error refreshing token",
            "error_code": "REFRESH_ERROR"
        }), 500