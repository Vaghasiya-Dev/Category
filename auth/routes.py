from flask import Blueprint, request, jsonify
from auth.models import UserRepository
from auth.auth_handler import AuthHandler
from auth.decorators import require_auth
from flask import current_app
from datetime import datetime
 
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
 
 
@auth_bp.route('/signup', methods=['POST'])
def signup():
    """
    Public signup endpoint

    Request Body:
        {
            "username": "string",
            "email": "string",
            "password": "string",
            "role": "emp" | "admin" | "super_admin"
        }
    """
    data = request.get_json()

    required_fields = {'username', 'email', 'password', 'role'}
    if not data or not required_fields.issubset(data):
        return jsonify({
            'success': False,
            'message': 'Missing required fields: username, email, password, role'
        }), 400

    if len(data['password']) < 6:
        return jsonify({
            'success': False,
            'message': 'Password must be at least 6 characters'
        }), 400

    role = data['role']
    if role not in ['emp', 'admin', 'super_admin']:
        return jsonify({
            'success': False,
            'message': 'Invalid role. Choose emp, admin, or super_admin'
        }), 400

    repo = UserRepository()
    user, message = repo.create_user(
        username=data['username'],
        email=data['email'],
        password=data['password'],
        role=role,
        created_by=None
    )

    if not user:
        return jsonify({'success': False, 'message': message}), 400

    access_token = AuthHandler.generate_token(user)
    refresh_token = AuthHandler.generate_refresh_token(user)

    return jsonify({
        'success': True,
        'message': message,
        'user': user,
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    User login endpoint
    
    Request Body:
        {
            "username": "string",
            "password": "string"
        }
    """
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({
            'success': False,
            'message': 'Username and password are required'
        }), 400
    
    username = data['username']
    password = data['password']
    
    repo = UserRepository()
    user = repo.find_by_username(username)
    
    if not user or not repo.verify_password(user, password):
        return jsonify({
            'success': False,
            'message': 'Invalid username or password'
        }), 401
    
    if user['status'] != 'active':
        return jsonify({
            'success': False,
            'message': 'Account is disabled'
        }), 403
    
    # Update last login time
    repo.update_last_login(user['user_id'])
    
    # Generate tokens
    access_token = AuthHandler.generate_token(user)
    refresh_token = AuthHandler.generate_refresh_token(user)
    
    return jsonify({
        'success': True,
        'message': 'Login successful',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {
            'user_id': user['user_id'],
            'username': user['username'],
            'email': user['email'],
            'role': user['role']
        }
    })
 
 
@auth_bp.route('/logout', methods=['POST'])
@require_auth
def logout(**kwargs):
    """
    User logout endpoint
    Note: Client-side should handle token invalidation
    """
    return jsonify({
        'success': True,
        'message': 'Logout successful'
    })
 
 
@auth_bp.route('/me', methods=['GET'])
@require_auth
def get_current_user_info(**kwargs):
    """Get current authenticated user information"""
    current_user = kwargs.get('current_user')
    return jsonify({
        'success': True,
        'user': {
            'user_id': current_user['user_id'],
            'username': current_user['username'],
            'email': current_user['email'],
            'role': current_user['role'],
            'created_by': current_user['created_by'],
            'status': current_user['status'],
            'created_at': current_user['created_at'],
            'last_login': current_user['last_login']
        }
    })
 
 
@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """
    Refresh access token using refresh token
    
    Request Body:
        {
            "refresh_token": "string"
        }
    """
    data = request.get_json()
    
    if not data or 'refresh_token' not in data:
        return jsonify({
            'success': False,
            'message': 'Refresh token is required'
        }), 400
    
    payload, error = AuthHandler.decode_token(data['refresh_token'])
    if error:
        return jsonify({
            'success': False,
            'message': error
        }), 401
    
    if payload.get('type') != 'refresh':
        return jsonify({
            'success': False,
            'message': 'Invalid token type'
        }), 401
    
    # Get user and generate new access token
    repo = UserRepository()
    user = repo.find_by_id(payload['user_id'])
    
    if not user:
        return jsonify({
            'success': False,
            'message': 'User not found'
        }), 404
    
    new_token = AuthHandler.generate_token(user)
    
    return jsonify({
        'success': True,
        'access_token': new_token
    })
 
 
@auth_bp.route('/change-password', methods=['POST'])
@require_auth
def change_password(**kwargs):
    """
    Change user password
    
    Request Body:
        {
            "old_password": "string",
            "new_password": "string"
        }
    """
    current_user = kwargs.get('current_user')
    data = request.get_json()
    
    if not data or 'old_password' not in data or 'new_password' not in data:
        return jsonify({
            'success': False,
            'message': 'Old password and new password are required'
        }), 400
    
    if len(data['new_password']) < 6:
        return jsonify({
            'success': False,
            'message': 'New password must be at least 6 characters'
        }), 400
    
    repo = UserRepository()
    
    # Verify old password
    if not repo.verify_password(current_user, data['old_password']):
        return jsonify({
            'success': False,
            'message': 'Old password is incorrect'
        }), 401
    
    # Update password
    from auth.models import User
    current_user['password_hash'] = User.hash_password(data['new_password'])
    current_user['updated_at'] = datetime.utcnow().isoformat()
    repo._save_data()
    
    return jsonify({
        'success': True,
        'message': 'Password changed successfully'
    })
