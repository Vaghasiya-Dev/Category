import os
from datetime import timedelta
 
class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # JWT configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Get the base directory (backend directory)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Database paths - use absolute paths
    USERS_DB_PATH = os.path.join(BASE_DIR, 'database', 'users.json')
    AUDIENCES_DB_PATH = os.path.join(BASE_DIR, 'database', 'audiences.json')
    CATEGORIES_DB_PATH = os.path.join(BASE_DIR, 'categories.json')
    BLOG_DB_PATH = os.path.join(BASE_DIR, 'database', 'blog.json')
    SETTINGS_DB_PATH = os.path.join(BASE_DIR, 'database', 'settings.json')
    
    # Role permissions configuration
    ROLES = {
        'super_admin': {
            'can_manage_users': True,
            'can_manage_admins': True,
            'can_manage_categories': True,
            'can_manage_audiences': True,
            'can_view_analytics': True
        },
        'admin': {
            'can_manage_users': True,
            'can_manage_admins': False,
            'can_manage_categories': False,
            'can_manage_audiences': True,
            'can_view_analytics': True
        },
        'emp': {
            'can_manage_users': False,
            'can_manage_admins': False,
            'can_manage_categories': False,
            'can_manage_audiences': False,
            'can_view_analytics': False
        }
    }
    
    # RBAC Permission Matrix - defines what each role can do to other roles
    # Format: {requester_role: {target_role: [allowed_actions]}}
    RBAC_MATRIX = {
        'super_admin': {
            'super_admin': ['view'],  # Can view other super admins but cannot modify
            'admin': ['create', 'view', 'update', 'delete', 'change_password'],
            'emp': ['create', 'view', 'update', 'delete', 'change_password']
        },
        'admin': {
            'super_admin': [],  # No access to super admins
            'admin': [],  # No access to other admins
            'emp': ['create', 'view', 'update', 'delete', 'change_password']
        },
        'emp': {
            'super_admin': [],
            'admin': [],
            'emp': []  # No access to manage anyone
        }
    }