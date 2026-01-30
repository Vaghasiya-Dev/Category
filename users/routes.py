from flask import Blueprint, request, jsonify
from users.services import UserService
from auth.decorators import require_auth, require_role
 
users_bp = Blueprint('users', __name__, url_prefix='/api/users')


def get_service():
    """Helper function to get UserService instance"""
    return UserService()


@users_bp.route('/emp', methods=['POST'])
@require_auth
@require_role('admin', 'super_admin')
def create_employee(**kwargs):
    """
    Create employee account (Admin and Super Admin can create employees)
    
    RBAC Rule: Admin and Super Admin can create Employee accounts
    
    Request Body:
        {
            "username": "string",
            "email": "string",
            "password": "string"
        }
    """
    current_user = kwargs.get('current_user')
    service = get_service()
    data = request.get_json()
    
    if not data or 'username' not in data or 'email' not in data or 'password' not in data:
        return jsonify({
            'success': False,
            'message': 'Missing required fields: username, email, password'
        }), 400
    
    if len(data['password']) < 6:
        return jsonify({
            'success': False,
            'message': 'Password must be at least 6 characters'
        }), 400
    
    user, message = service.create_employee(
        username=data['username'],
        email=data['email'],
        password=data['password'],
        created_by=current_user['user_id']
    )
    
    if not user:
        return jsonify({
            'success': False,
            'message': message
        }), 400
    
    return jsonify({
        'success': True,
        'message': message,
        'user': user
    }), 201
 
 
@users_bp.route('/admin', methods=['POST'])
@require_auth
@require_role('super_admin')
def create_admin(**kwargs):
    """
    Create admin account (Super Admin only)
    
    RBAC Rule: Only Super Admin can create Administrator accounts
    
    Request Body:
        {
            "username": "string",
            "email": "string",
            "password": "string"
        }
    """
    current_user = kwargs.get('current_user')
    service = get_service()
    data = request.get_json()
    
    if not data or 'username' not in data or 'email' not in data or 'password' not in data:
        return jsonify({
            'success': False,
            'message': 'Missing required fields: username, email, password'
        }), 400
    
    if len(data['password']) < 6:
        return jsonify({
            'success': False,
            'message': 'Password must be at least 6 characters'
        }), 400
    
    user, message = service.create_admin(
        username=data['username'],
        email=data['email'],
        password=data['password'],
        created_by=current_user['user_id']
    )
    
    if not user:
        return jsonify({
            'success': False,
            'message': message
        }), 400
    
    return jsonify({
        'success': True,
        'message': message,
        'user': user
    }), 201
 
 
@users_bp.route('/', methods=['GET'])
@require_auth
def get_all_users(**kwargs):
    """
    Get list of users based on RBAC permissions
    
    RBAC Rules:
    - Super Admin: Can view Admin and Employee users (not other Super Admins)
    - Admin: Can view Employee users only
    - Employee: Cannot view other users
    
    Query Params:
        role: Filter by role (optional)
        status: Filter by status (optional)
    """
    current_user = kwargs.get('current_user')
    service = get_service()
    users = service.get_users_list(current_user['role'])
    
    # Apply filters if provided
    role_filter = request.args.get('role')
    status_filter = request.args.get('status')
    
    if role_filter:
        users = [u for u in users if u['role'] == role_filter]
    
    if status_filter:
        users = [u for u in users if u['status'] == status_filter]
    
    return jsonify({
        'success': True,
        'users': users,
        'count': len(users)
    })
 
 
@users_bp.route('/<user_id>', methods=['GET'])
@require_auth
def get_user(**kwargs):
    """
    Get user by ID with RBAC permission checks
    
    RBAC Rules: Can only view users you have permission to access
    """
    current_user = kwargs.get('current_user')
    user_id = kwargs.get('user_id')
    service = get_service()
    user, error = service.get_user_by_id(
        user_id=user_id,
        requester_role=current_user['role'],
        requester_id=current_user['user_id']
    )
    
    if error:
        return jsonify({
            'success': False,
            'message': error
        }), 403 if "denied" in error else 404
    
    return jsonify({
        'success': True,
        'user': user
    })
 
 
@users_bp.route('/<user_id>/status', methods=['PUT'])
@require_auth
@require_role('admin', 'super_admin')
def update_user_status(**kwargs):
    """
    Update user status with RBAC checks
    
    RBAC Rules:
    - Super Admin: Can update status of Admin and Employee users
    - Admin: Can update status of Employee users only
    
    Request Body:
        {
            "status": "active" | "inactive"
        }
    """
    current_user = kwargs.get('current_user')
    user_id = kwargs.get('user_id')
    service = get_service()
    data = request.get_json()
    
    if not data or 'status' not in data:
        return jsonify({
            'success': False,
            'message': 'Missing required field: status'
        }), 400
    
    if data['status'] not in ['active', 'inactive']:
        return jsonify({
            'success': False,
            'message': 'Invalid status. Must be active or inactive'
        }), 400
    
    success, message = service.update_user_status(
        user_id=user_id,
        status=data['status'],
        requester_role=current_user['role'],
        requester_id=current_user['user_id']
    )
    
    if not success:
        return jsonify({
            'success': False,
            'message': message
        }), 403
    
    return jsonify({
        'success': True,
        'message': message
    })
 
 
@users_bp.route('/statistics', methods=['GET'])
@require_auth
@require_role('admin', 'super_admin')
def get_user_statistics(**kwargs):
    """Get user statistics (Admin and Super Admin)"""
    current_user = kwargs.get('current_user')
    service = get_service()
    stats = service.get_user_statistics()
    
    return jsonify({
        'success': True,
        'statistics': stats
    })


@users_bp.route('/<user_id>', methods=['PUT'])
@require_auth
def update_user_profile(**kwargs):
    """
    Update user profile information with RBAC checks
    
    RBAC Rules:
    - Super Admin: Can update Admin and Employee profiles
    - Admin: Can update Employee profiles only
    - Employee: Can only update their own profile
    
    Request Body:
        {
            "username": "string" (optional),
            "email": "string" (optional)
        }
    """
    current_user = kwargs.get('current_user')
    user_id = kwargs.get('user_id')
    service = get_service()
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'message': 'No data provided'
        }), 400
    
    allowed_fields = ['username', 'email']
    updates = {k: v for k, v in data.items() if k in allowed_fields}
    
    if not updates:
        return jsonify({
            'success': False,
            'message': 'No valid fields to update'
        }), 400
    
    user, error = service.update_user_profile(
        user_id=user_id,
        updates=updates,
        requester_role=current_user['role'],
        requester_id=current_user['user_id']
    )
    
    if error:
        return jsonify({
            'success': False,
            'message': error
        }), 403 if "denied" in error or "permission" in error else 400
    
    return jsonify({
        'success': True,
        'message': 'User updated successfully',
        'user': user
    })


@users_bp.route('/<user_id>/password', methods=['PUT'])
@require_auth
def update_password(**kwargs):
    """
    Update user password with RBAC checks
    
    RBAC Rules:
    - Super Admin: Can change passwords for Admin and Employee users
    - Admin: Can change passwords for Employee users only
    - Employee: Can only change their own password
    
    Request Body:
        {
            "old_password": "string" (required if changing own password),
            "new_password": "string"
        }
    """
    current_user = kwargs.get('current_user')
    user_id = kwargs.get('user_id')
    service = get_service()
    data = request.get_json()
    
    if not data or 'new_password' not in data:
        return jsonify({
            'success': False,
            'message': 'new_password is required'
        }), 400
    
    # If user is changing their own password, old_password is required
    old_password = data.get('old_password', '')
    if user_id == current_user['user_id'] and not old_password:
        return jsonify({
            'success': False,
            'message': 'old_password is required when changing your own password'
        }), 400
    
    success, message = service.update_password(
        user_id=user_id,
        old_password=old_password,
        new_password=data['new_password'],
        requester_role=current_user['role'],
        requester_id=current_user['user_id']
    )
    
    if not success:
        return jsonify({
            'success': False,
            'message': message
        }), 403 if "permission" in message else 400
    
    return jsonify({
        'success': True,
        'message': message
    })


@users_bp.route('/<user_id>', methods=['DELETE'])
@require_auth
@require_role('admin', 'super_admin')
def delete_user(**kwargs):
    """
    Delete user (soft delete - sets status to inactive) with RBAC enforcement
    
    RBAC Rules:
    - Super Admin: Can delete Admin and Employee users (cannot delete other Super Admins)
    - Admin: Can delete Employee users only (cannot delete Admin or Super Admin)
    - Employee: Cannot delete any users
    """
    current_user = kwargs.get('current_user')
    user_id = kwargs.get('user_id')
    service = get_service()
    
    success, message = service.delete_user(
        user_id=user_id,
        requester_role=current_user['role'],
        requester_id=current_user['user_id']
    )
    
    if not success:
        return jsonify({
            'success': False,
            'message': message
        }), 403
    
    return jsonify({
        'success': True,
        'message': message
    })


@users_bp.route('/validate-permission', methods=['POST'])
@require_auth
def validate_permission(**kwargs):
    """
    Validate if user has permission to perform action on target role
    
    Request Body:
        {
            "target_role": "emp" | "admin" | "super_admin",
            "action": "create" | "update" | "delete" | "view"
        }
    """
    current_user = kwargs.get('current_user')
    service = get_service()
    data = request.get_json()
    
    if not data or 'target_role' not in data or 'action' not in data:
        return jsonify({
            'success': False,
            'message': 'target_role and action are required'
        }), 400
    
    allowed, message = service.validate_role_permission(
        requester_role=current_user['role'],
        target_role=data['target_role'],
        action=data['action']
    )
    
    return jsonify({
        'success': True,
        'allowed': allowed,
        'message': message
    })
