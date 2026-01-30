"""
Dashboard Page Handler
Handles dashboard rendering and user profile data
"""
from flask import Blueprint, render_template, jsonify, current_app
from auth.models import UserRepository
from auth.decorators import require_auth

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard-handler')


class DashboardService:
    """Business logic for dashboard page"""
    
    def __init__(self):
        self.user_repo = UserRepository(current_app.config['USERS_DB_PATH'])
    
    def get_user_profile(self, user_id):
        """Get user profile data"""
        user = self.user_repo.find_by_id(user_id)
        if not user:
            return None, "User not found"
        
        return {
            'user_id': user['user_id'],
            'username': user['username'],
            'email': user['email'],
            'role': user['role'],
            'status': user['status'],
            'created_at': user['created_at'],
            'last_login': user['last_login']
        }, None
    
    def get_dashboard_modules(self, role):
        """Get available modules based on role"""
        modules = {
            'profile': {
                'title': '👤 My Profile',
                'description': 'View and edit your profile',
                'url': '/dashboard#profile',
                'available_roles': ['emp', 'admin', 'super_admin'],
                'permissions': ['view_own_profile', 'edit_own_profile']
            },
            'blog': {
                'title': '📝 Blog',
                'description': 'Manage blog content',
                'url': '/blog-page',
                'available_roles': ['admin', 'super_admin', 'emp'],
                'permissions': ['view_blog']
            },
            'settings': {
                'title': '⚙️ Settings',
                'description': 'Manage application settings',
                'url': '/settings-page',
                'available_roles': ['admin', 'super_admin'],
                'permissions': ['manage_settings']
            },
            'categories': {
                'title': '📂 Categories',
                'description': 'Browse hierarchical categories',
                'url': '/category-page',
                'available_roles': ['admin', 'super_admin', 'emp'],
                'permissions': ['view_categories']
            },
            'admin': {
                'title': '👤 Admin Panel',
                'description': 'Manage users and audiences',
                'url': '/admin',
                'available_roles': ['admin', 'super_admin'],
                'permissions': ['manage_users', 'view_statistics']
            },
            'audiences': {
                'title': '👥 Audiences',
                'description': 'Manage audience segments',
                'url': '/audiences',
                'available_roles': ['admin', 'super_admin'],
                'permissions': ['manage_audiences']
            }
        }
        
        # Filter modules by role
        available = {
            k: v for k, v in modules.items() 
            if role in v['available_roles']
        }
        
        return available
    
    def get_user_capabilities(self, role):
        """Get user capabilities based on role"""
        capabilities = {
            'emp': {
                'can_view_own_profile': True,
                'can_edit_own_profile': True,
                'can_change_own_password': True,
                'can_view_blog': True,
                'can_edit_blog': False,
                'can_view_categories': True,
                'can_manage_categories': False,
                'can_view_settings': False,
                'can_manage_settings': False,
                'can_access_admin_panel': False,
                'dashboard_widgets': ['profile', 'blog', 'categories']
            },
            'admin': {
                'can_view_own_profile': True,
                'can_edit_own_profile': True,
                'can_change_own_password': True,
                'can_view_blog': True,
                'can_edit_blog': True,
                'can_view_categories': True,
                'can_manage_categories': False,
                'can_view_settings': True,
                'can_manage_settings': True,
                'can_access_admin_panel': True,
                'can_create_employees': True,
                'can_manage_employees': True,
                'can_view_statistics': True,
                'dashboard_widgets': ['profile', 'users', 'blog', 'categories', 'settings', 'statistics']
            },
            'super_admin': {
                'can_view_own_profile': True,
                'can_edit_own_profile': True,
                'can_change_own_password': True,
                'can_view_blog': True,
                'can_edit_blog': True,
                'can_view_categories': True,
                'can_manage_categories': True,
                'can_view_settings': True,
                'can_manage_settings': True,
                'can_access_admin_panel': True,
                'can_create_employees': True,
                'can_create_admins': True,
                'can_manage_employees': True,
                'can_manage_admins': True,
                'can_view_statistics': True,
                'dashboard_widgets': ['profile', 'users', 'admins', 'blog', 'categories', 'settings', 'statistics', 'audiences']
            }
        }
        return capabilities.get(role, {})


@dashboard_bp.route('/profile', methods=['GET'])
@require_auth
def get_profile(**kwargs):
    """Get current user profile"""
    current_user = kwargs.get('current_user')
    service = DashboardService()
    profile, error = service.get_user_profile(current_user['user_id'])
    
    if error:
        return jsonify({'success': False, 'message': error}), 404
    
    return jsonify({
        'success': True,
        'profile': profile
    })


@dashboard_bp.route('/modules', methods=['GET'])
@require_auth
def get_available_modules(**kwargs):
    """Get available modules for user role"""
    current_user = kwargs.get('current_user')
    service = DashboardService()
    modules = service.get_dashboard_modules(current_user['role'])
    
    return jsonify({
        'success': True,
        'modules': modules,
        'user_role': current_user['role']
    })


@dashboard_bp.route('/capabilities', methods=['GET'])
@require_auth
def get_user_capabilities(**kwargs):
    """Get user capabilities based on role"""
    current_user = kwargs.get('current_user')
    service = DashboardService()
    capabilities = service.get_user_capabilities(current_user['role'])
    
    return jsonify({
        'success': True,
        'capabilities': capabilities,
        'user_role': current_user['role']
    })


@dashboard_bp.route('/')
def dashboard_page():
    """Render dashboard page"""
    return render_template('dashboard.html')
