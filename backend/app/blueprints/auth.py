from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from marshmallow import ValidationError
from app.models import User
from app.schemas import LoginSchema, UserSchema
from app.utils.decorators import audit_log
from app import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
@audit_log('login_attempt')
def login():
    """
    User login endpoint
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: credentials
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              format: email
            password:
              type: string
    responses:
      200:
        description: Login successful
      401:
        description: Invalid credentials
    """
    try:
        schema = LoginSchema()
        data = schema.load(request.json)
        
        user = User.query.filter_by(email=data['email'], is_active=True).first()
        
        if user and user.check_password(data['password']):
            access_token = create_access_token(identity=user.id)
            user_schema = UserSchema()
            return jsonify({
                'access_token': access_token,
                'user': user_schema.dump(user)
            }), 200
        
        return jsonify({'message': 'Invalid credentials'}), 401
    
    except ValidationError as e:
        return jsonify({'errors': e.messages}), 400

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Get current user profile
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: User profile
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_active:
        return jsonify({'message': 'User not found'}), 404
    
    schema = UserSchema()
    return jsonify(schema.dump(user)), 200