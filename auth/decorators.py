from flask import request, jsonify, current_app
from auth.auth_handler import AuthHandler
from functools import wraps


def require_auth(f):
    """
    Authentication decorator - requires valid JWT token
    
    Usage:
        @require_auth
        def protected_route(current_user):
            return jsonify({'user': current_user})
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({
                'success': False,
                'message': 'Authentication token is required'
            }), 401
        
        user, error = AuthHandler.get_current_user(token)
        if error:
            return jsonify({
                'success': False,
                'message': error
            }), 401
        
        return f(current_user=user, *args, **kwargs)
    
    return decorated


def require_role(*allowed_roles):
    """
    Role-based access control decorator
    
    Usage:
        @require_role('admin', 'super_admin')
        def admin_only_route(current_user):
            return jsonify({'message': 'Admin access'})
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                return jsonify({
                    'success': False,
                    'message': 'Authentication required'
                }), 401
                
            if current_user['role'] not in allowed_roles:
                return jsonify({
                    'success': False,
                    'message': f'Access denied. Required roles: {", ".join(allowed_roles)}'
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated
    return decorator


def check_permission(permission):
    """
    Permission-based access control decorator
    
    Usage:
        @check_permission('can_manage_categories')
        def category_management(current_user):
            return jsonify({'message': 'Category management'})
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                return jsonify({
                    'success': False,
                    'message': 'Authentication required'
                }), 401
                
            roles = current_app.config['ROLES']
            user_permissions = roles.get(current_user['role'], {})
            
            if not user_permissions.get(permission, False):
                return jsonify({
                    'success': False,
                    'message': f'Permission denied: {permission}'
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated
    return decorator


def check_rbac_permission(action):
    """
    RBAC permission decorator - validates if requester can perform action on target user
    
    Args:
        action: The action to perform ('create', 'view', 'update', 'delete', 'change_password')
    
    Usage:
        @check_rbac_permission('update')
        def update_user(current_user, target_user):
            # Validates current_user can update target_user
            pass
    
    Note: This decorator requires validate_target_user_access to be used first
    to inject the target_user into kwargs
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            current_user = kwargs.get('current_user')
            target_user = kwargs.get('target_user')
            
            if not current_user:
                return jsonify({
                    'success': False,
                    'message': 'Authentication required'
                }), 401
            
            if not target_user:
                return jsonify({
                    'success': False,
                    'message': 'Target user not found'
                }), 404
            
            # Get RBAC matrix from config
            rbac_matrix = current_app.config.get('RBAC_MATRIX', {})
            requester_role = current_user['role']
            target_role = target_user['role']
            
            # Check if requester can perform action on target role
            allowed_actions = rbac_matrix.get(requester_role, {}).get(target_role, [])
            
            if action not in allowed_actions:
                return jsonify({
                    'success': False,
                    'message': f'You do not have permission to {action} {target_role} users'
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated
    return decorator


def check_ownership_or_admin(f):
    """
    Check if user owns the resource or is admin/super_admin
    
    Usage:
        @check_ownership_or_admin
        def update_user(current_user, user_id):
            # User can only update their own profile unless they're admin
            pass
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        current_user = kwargs.get('current_user')
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Authentication required'
            }), 401
            
        resource_owner_id = kwargs.get('user_id')
        
        # Allow if user is admin or super_admin
        if current_user['role'] in ['admin', 'super_admin']:
            return f(*args, **kwargs)
        
        # Allow if user is accessing their own data
        if resource_owner_id == current_user['user_id']:
            return f(*args, **kwargs)
        
        return jsonify({
            'success': False,
            'message': 'Access denied. You can only access your own data.'
        }), 403
    
    return decorated


def require_role_hierarchy(min_role):
    """
    Hierarchical role-based access control decorator
    Enforces role hierarchy: super_admin > admin > emp
    
    Args:
        min_role: Minimum role required ('emp', 'admin', 'super_admin')
    
    Usage:
        @require_role_hierarchy('admin')
        def admin_or_higher(current_user):
            # Allows admin and super_admin only
            pass
    """
    role_hierarchy = {
        'emp': 0,
        'admin': 1,
        'super_admin': 2
    }
    
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                return jsonify({
                    'success': False,
                    'message': 'Authentication required'
                }), 401
                
            user_role_level = role_hierarchy.get(current_user['role'], -1)
            required_level = role_hierarchy.get(min_role, 999)
            
            if user_role_level < required_level:
                return jsonify({
                    'success': False,
                    'message': f'Access denied. Minimum role required: {min_role}'
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated
    return decorator


def validate_target_user_access(f):
    """
    Validate access to target user based on role hierarchy
    
    This decorator checks if the current user has permission to access/modify
    the target user specified in the route parameter 'user_id'.
    
    Rules:
    - Super Admin: Can access/modify admin and emp users (not other super admins)
    - Admin: Can access/modify emp users only
    - Emp: Can only access/modify their own profile
    
    Usage:
        @validate_target_user_access
        def modify_user(current_user, user_id, target_user):
            # target_user is injected by this decorator
            pass
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        from auth.models import UserRepository
        from flask import current_app
        
        current_user = kwargs.get('current_user')
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Authentication required'
            }), 401
        
        user_id = kwargs.get('user_id')
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'User ID is required'
            }), 400
        
        # Get target user
        repo = UserRepository()
        target_user = repo.find_by_id(user_id)
        
        if not target_user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        requester_role = current_user['role']
        target_role = target_user['role']
        
        # Self access always allowed
        if user_id == current_user['user_id']:
            kwargs['target_user'] = target_user
            return f(*args, **kwargs)
        
        # Employee cannot access other users
        if requester_role == 'emp':
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403
        
        # Admin can only access emp users
        if requester_role == 'admin' and target_role != 'emp':
            return jsonify({
                'success': False,
                'message': 'Cannot access users of this role'
            }), 403
        
        # Super admin cannot access other super admins
        if requester_role == 'super_admin' and target_role == 'super_admin':
            return jsonify({
                'success': False,
                'message': 'Cannot access other super admins'
            }), 403
        
        # Access granted, inject target_user
        kwargs['target_user'] = target_user
        return f(*args, **kwargs)
    
    return decorated
