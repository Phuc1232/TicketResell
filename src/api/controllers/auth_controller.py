from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from marshmallow import Schema, fields, validate
from datetime import datetime, timedelta

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Schemas
class LoginSchema(Schema):
    email = fields.Email(required=True, error_messages={"required": "Email is required"})
    password = fields.Str(required=True, validate=validate.Length(min=6),
                         error_messages={"required": "Password is required",
                                        "validator_failed": "Password must be at least 6 characters"})

class RegisterSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50),
                         error_messages={"required": "Username is required",
                                        "validator_failed": "Username must be between 3 and 50 characters"})
    email = fields.Email(required=True, error_messages={"required": "Email is required"})
    password = fields.Str(required=True, validate=validate.Length(min=6),
                         error_messages={"required": "Password is required",
                                        "validator_failed": "Password must be at least 6 characters"})
    phone_number = fields.Str(validate=validate.Length(min=10, max=15))

login_schema = LoginSchema()
register_schema = RegisterSchema()

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
          content:
            application/json:
              schema:
                type: object
                properties:
                  access_token:
                    type: string
                  message:
                    type: string
        401:
          description: Invalid credentials
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "No data provided"}), 400
            
        errors = login_schema.validate(data)
        if errors:
            return jsonify({"message": "Validation errors", "errors": errors}), 400
        
        email = data['email']
        password = data['password']
        
        # TODO: Implement actual authentication logic
        # 1. Check if user exists
        # 2. Verify password
        # 3. Generate JWT token
        
        # Mock authentication for now
        if email == "test@example.com" and password == "password123":
            access_token = create_access_token(identity=1, expires_delta=timedelta(hours=24))
            return jsonify({
                "access_token": access_token,
                "message": "Login successful"
            }), 200
        else:
            return jsonify({"message": "Invalid credentials"}), 401
            
    except Exception as e:
        return jsonify({"message": "Error during login", "error": str(e)}), 500

@bp.route('/register', methods=['POST'])
def register():
    """
    User registration
    ---
    post:
      summary: User registration
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                username:
                  type: string
                  description: Username
                email:
                  type: string
                  format: email
                  description: User email
                password:
                  type: string
                  description: User password
                phone_number:
                  type: string
                  description: Phone number
              required:
                - username
                - email
                - password
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
                  message:
                    type: string
        400:
          description: Invalid input data
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
        
        username = data['username']
        email = data['email']
        password = data['password']
        phone_number = data.get('phone_number')
        
        # TODO: Implement actual registration logic
        # 1. Check if user already exists
        # 2. Hash password
        # 3. Create user record
        # 4. Send verification email
        
        return jsonify({
            "user_id": 1,
            "message": "Registration successful"
        }), 201
        
    except Exception as e:
        return jsonify({"message": "Error during registration", "error": str(e)}), 500

@bp.route('/verify', methods=['POST'])
@jwt_required()
def verify_token():
    """
    Verify JWT token
    ---
    post:
      summary: Verify JWT token
      security:
        - BearerAuth: []
      tags:
        - Authentication
      responses:
        200:
          description: Token is valid
          content:
            application/json:
              schema:
                type: object
                properties:
                  user_id:
                    type: integer
                  message:
                    type: string
        401:
          description: Invalid token
    """
    try:
        current_user_id = get_jwt_identity()
        return jsonify({
            "user_id": current_user_id,
            "message": "Token is valid"
        }), 200
        
    except Exception as e:
        return jsonify({"message": "Invalid token", "error": str(e)}), 401