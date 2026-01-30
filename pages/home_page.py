"""
Home Page Handler
Handles home page rendering and portal information
"""
from flask import Blueprint, render_template, jsonify, current_app
from auth.decorators import require_auth

home_page_bp = Blueprint('home_page', __name__, url_prefix='/home-handler')


class HomePageService:
    """Business logic for home page"""
    
    def __init__(self):
        self.app_name = 'Role-Based Portal'
        self.app_version = '1.0.0'
    
    def get_page_info(self):
        """Get home page information"""
        return {
            'title': '🏠 Welcome to Role-Based Portal',
            'subtitle': 'Manage categories, blog, settings & more',
            'description': 'A comprehensive role-based access control application'
        }
    
    def get_available_pages(self, user_role=None):
        """Get available pages based on user role"""
        all_pages = [
            {
                'name': 'Dashboard',
                'route': '/dashboard',
                'icon': '📊',
                'description': 'View your profile and dashboard',
                'required_role': 'emp',
                'enabled': True
            },
            {
                'name': 'Blog',
                'route': '/blog',
                'icon': '📝',
                'description': 'Create and manage blog posts',
                'required_role': 'emp',
                'enabled': True
            },
            {
                'name': 'Categories',
                'route': '/categories',
                'icon': '📂',
                'description': 'Manage product categories',
                'required_role': 'admin',
                'enabled': True
            },
            {
                'name': 'Settings',
                'route': '/settings',
                'icon': '⚙️',
                'description': 'Customize application settings',
                'required_role': 'admin',
                'enabled': True
            },
            {
                'name': 'Admin Panel',
                'route': '/admin',
                'icon': '👤',
                'description': 'Manage users and audiences',
                'required_role': 'admin',
                'enabled': True
            }
        ]
        
        # Filter pages based on user role
        if user_role:
            role_hierarchy = {'emp': 0, 'admin': 1, 'super_admin': 2}
            user_level = role_hierarchy.get(user_role, -1)
            
            filtered_pages = []
            for page in all_pages:
                page_level = role_hierarchy.get(page['required_role'], -1)
                if user_level >= page_level:
                    filtered_pages.append(page)
            
            return filtered_pages
        
        return all_pages
    
    def get_system_info(self):
        """Get system information"""
        return {
            'app_name': self.app_name,
            'version': self.app_version,
            'features': [
                'Role-Based Access Control (RBAC)',
                'JWT Authentication',
                'Blog Management',
                'Category Management',
                'User Management',
                'Settings Management',
                'Audience Management'
            ]
        }
    
    def get_architecture_overview(self):
        """Get application architecture overview"""
        return {
            'frontend': {
                'technology': 'HTML5, CSS3, JavaScript',
                'pages': 7,
                'authentication': 'JWT in localStorage',
                'communication': 'Fetch API / REST'
            },
            'backend': {
                'technology': 'Flask, Python',
                'architecture': 'Blueprint-based modular design',
                'authentication': 'JWT with decorators',
                'database': 'JSON-based storage'
            },
            'rbac': {
                'roles': ['emp', 'admin', 'super_admin'],
                'hierarchy': 'emp < admin < super_admin',
                'enforcement': 'Decorator-based authorization'
            }
        }
    
    def get_home_permissions(self, user_role):
        """Get home page permissions based on role"""
        permissions = {
            'emp': {
                'can_view_home': True,
                'can_view_system_info': True,
                'can_access_dashboard': True,
                'can_access_blog': True,
                'can_access_categories': True,
                'can_access_settings': False,
                'can_access_admin': False
            },
            'admin': {
                'can_view_home': True,
                'can_view_system_info': True,
                'can_access_dashboard': True,
                'can_access_blog': True,
                'can_access_categories': True,
                'can_access_settings': True,
                'can_access_admin': True
            },
            'super_admin': {
                'can_view_home': True,
                'can_view_system_info': True,
                'can_access_dashboard': True,
                'can_access_blog': True,
                'can_access_categories': True,
                'can_access_settings': True,
                'can_access_admin': True
            }
        }
        return permissions.get(user_role, {})


@home_page_bp.route('/info', methods=['GET'])
def get_page_info():
    """Get home page information"""
    service = HomePageService()
    info = service.get_page_info()
    
    return jsonify({
        'success': True,
        'info': info
    })


@home_page_bp.route('/pages', methods=['GET'])
def get_available_pages():
    """Get available pages"""
    service = HomePageService()
    pages = service.get_available_pages()
    
    return jsonify({
        'success': True,
        'pages': pages
    })


@home_page_bp.route('/pages-for-user', methods=['GET'])
@require_auth
def get_pages_for_user(**kwargs):
    """Get available pages for authenticated user"""
    current_user = kwargs.get('current_user')
    service = HomePageService()
    pages = service.get_available_pages(current_user['role'])
    
    return jsonify({
        'success': True,
        'user_role': current_user['role'],
        'pages': pages
    })


@home_page_bp.route('/system-info', methods=['GET'])
def get_system_info():
    """Get system information"""
    service = HomePageService()
    info = service.get_system_info()
    
    return jsonify({
        'success': True,
        'system': info
    })


@home_page_bp.route('/architecture', methods=['GET'])
def get_architecture_info():
    """Get architecture overview"""
    service = HomePageService()
    architecture = service.get_architecture_overview()
    
    return jsonify({
        'success': True,
        'architecture': architecture
    })


@home_page_bp.route('/permissions', methods=['GET'])
@require_auth
def get_home_permissions(**kwargs):
    """Get home page permissions for current user"""
    current_user = kwargs.get('current_user')
    service = HomePageService()
    permissions = service.get_home_permissions(current_user['role'])
    
    return jsonify({
        'success': True,
        'role': current_user['role'],
        'permissions': permissions
    })


@home_page_bp.route('/')
def home_page():
    """Render home page"""
    return render_template('home.html')
