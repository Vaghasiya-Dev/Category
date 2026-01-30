"""
Admin Panel Page Handler
Handles admin panel rendering and admin operations
"""
from flask import Blueprint, render_template, jsonify, current_app
from users.services import UserService
from audiences.services import AudienceService
from auth.decorators import require_auth, require_role

admin_page_bp = Blueprint('admin_page', __name__, url_prefix='/admin-handler')


class AdminPageService:
    """Business logic for admin page"""
    
    def __init__(self):
        self.user_service = UserService()
        self.audience_service = AudienceService()
    
    def get_users_for_admin(self, requester_role):
        """Get users list based on admin level"""
        users = self.user_service.get_users_list(requester_role)
        return users
    
    def get_admin_statistics(self):
        """Get admin statistics"""
        stats = self.user_service.get_user_statistics()
        return stats
    
    def get_audiences_overview(self):
        """Get audiences overview"""
        audiences = self.audience_service.get_all_audiences()
        return {
            'total': len(audiences) if audiences else 0,
            'audiences': audiences
        }
    
    def validate_admin_access(self, user_role):
        """Validate if user can access admin panel"""
        allowed_roles = ['admin', 'super_admin']
        can_access = user_role in allowed_roles
        return can_access, "Access denied"
    
    def get_admin_capabilities(self, user_role):
        """Get admin capabilities based on role using RBAC matrix"""
        from flask import current_app
        rbac_matrix = current_app.config.get('RBAC_MATRIX', {})
        role_permissions = rbac_matrix.get(user_role, {})
        
        # Build capabilities from RBAC matrix
        capabilities = {
            # Employee permissions
            'can_create_emp': 'create' in role_permissions.get('emp', []),
            'can_view_emp': 'view' in role_permissions.get('emp', []),
            'can_edit_emp': 'update' in role_permissions.get('emp', []),
            'can_delete_emp': 'delete' in role_permissions.get('emp', []),
            'can_change_emp_password': 'change_password' in role_permissions.get('emp', []),
            
            # Admin permissions
            'can_create_admin': 'create' in role_permissions.get('admin', []),
            'can_view_admin': 'view' in role_permissions.get('admin', []),
            'can_edit_admin': 'update' in role_permissions.get('admin', []),
            'can_delete_admin': 'delete' in role_permissions.get('admin', []),
            'can_change_admin_password': 'change_password' in role_permissions.get('admin', []),
            
            # Super Admin permissions
            'can_view_super_admin': 'view' in role_permissions.get('super_admin', []),
            
            # Additional permissions from config
            'can_manage_audiences': current_app.config['ROLES'].get(user_role, {}).get('can_manage_audiences', False),
            'can_view_audiences': current_app.config['ROLES'].get(user_role, {}).get('can_manage_audiences', False),
            'can_view_statistics': user_role in ['admin', 'super_admin'],
            'can_manage_categories': current_app.config['ROLES'].get(user_role, {}).get('can_manage_categories', False)
        }
        
        return capabilities
    
    def get_admin_metadata(self):
        """Get admin page metadata"""
        return {
            'page_title': '👤 Admin Panel',
            'page_description': 'Manage users and audiences',
            'tabs': [
                {'id': 'users', 'label': 'Users', 'icon': '👤'},
                {'id': 'audiences', 'label': 'Audiences', 'icon': '👥'},
                {'id': 'stats', 'label': 'Statistics', 'icon': '📊'}
            ]
        }
    
    def check_user_action_permission(self, requester_role, target_role, action):
        """Check if requester can perform action on target user using RBAC matrix"""
        from flask import current_app
        rbac_matrix = current_app.config.get('RBAC_MATRIX', {})
        
        # Map action names
        action_map = {
            'edit': 'update',
            'change_password': 'change_password',
            'delete': 'delete',
            'view': 'view',
            'create': 'create'
        }
        
        normalized_action = action_map.get(action, action)
        
        # Get allowed actions for this role combination
        allowed_actions = rbac_matrix.get(requester_role, {}).get(target_role, [])
        
        if normalized_action in allowed_actions:
            return True, "Action allowed"
        else:
            return False, f"You do not have permission to {action} {target_role} users"


@admin_page_bp.route('/validate-access', methods=['GET'])
@require_auth
def validate_admin_access(**kwargs):
    """Validate admin access"""
    current_user = kwargs.get('current_user')
    service = AdminPageService()
    can_access, message = service.validate_admin_access(current_user['role'])
    
    if not can_access:
        return jsonify({'success': False, 'message': message}), 403
    
    return jsonify({'success': True, 'message': 'Access granted'})


@admin_page_bp.route('/capabilities', methods=['GET'])
@require_auth
def get_admin_capabilities(**kwargs):
    """Get admin capabilities"""
    current_user = kwargs.get('current_user')
    service = AdminPageService()
    can_access, _ = service.validate_admin_access(current_user['role'])
    
    if not can_access:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    capabilities = service.get_admin_capabilities(current_user['role'])
    
    return jsonify({
        'success': True,
        'user_role': current_user['role'],
        'capabilities': capabilities
    })


@admin_page_bp.route('/users-overview', methods=['GET'])
@require_auth
@require_role('admin', 'super_admin')
def get_users_overview(**kwargs):
    """Get users overview"""
    current_user = kwargs.get('current_user')
    service = AdminPageService()
    users = service.get_users_for_admin(current_user['role'])
    
    return jsonify({
        'success': True,
        'users': users,
        'count': len(users)
    })


@admin_page_bp.route('/statistics', methods=['GET'])
@require_auth
@require_role('admin', 'super_admin')
def get_admin_statistics(**kwargs):
    """Get admin statistics"""
    current_user = kwargs.get('current_user')
    service = AdminPageService()
    stats = service.get_admin_statistics()
    
    return jsonify({
        'success': True,
        'statistics': stats
    })


@admin_page_bp.route('/audiences-overview', methods=['GET'])
@require_auth
@require_role('admin', 'super_admin')
def get_audiences_overview(**kwargs):
    """Get audiences overview"""
    current_user = kwargs.get('current_user')
    service = AdminPageService()
    overview = service.get_audiences_overview()
    
    return jsonify({
        'success': True,
        'overview': overview
    })


@admin_page_bp.route('/metadata', methods=['GET'])
def get_admin_metadata():
    """Get admin page metadata"""
    service = AdminPageService()
    metadata = service.get_admin_metadata()
    
    return jsonify({
        'success': True,
        'metadata': metadata
    })


@admin_page_bp.route('/check-action-permission', methods=['POST'])
@require_auth
@require_role('admin', 'super_admin')
def check_action_permission(**kwargs):
    """Check if user can perform action on target user"""
    from flask import request
    
    current_user = kwargs.get('current_user')
    data = request.get_json()
    if not data or 'target_role' not in data or 'action' not in data:
        return jsonify({
            'success': False,
            'message': 'target_role and action are required'
        }), 400
    
    service = AdminPageService()
    allowed, message = service.check_user_action_permission(
        current_user['role'],
        data['target_role'],
        data['action']
    )
    
    return jsonify({
        'success': True,
        'allowed': allowed,
        'message': message
    })


@admin_page_bp.route('/')
def admin_page():
    """Render admin page"""
    return render_template('admin_panel.html')
