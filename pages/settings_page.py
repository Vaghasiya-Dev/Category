"""
Settings Page Handler
Handles settings page rendering and settings operations
"""
from flask import Blueprint, render_template, jsonify, request, current_app
import jwt
from config import Config
from settings.services import SettingsService
from auth.decorators import require_auth

settings_page_bp = Blueprint('settings_page', __name__, url_prefix='/settings-handler')


class SettingsPageService:
    """Business logic for settings page"""
    
    def __init__(self):
        self.settings_service = SettingsService()
    
    def get_available_settings(self):
        """Get all available settings options"""
        return {
            'themes': [
                {'value': 'login-style', 'label': 'Login Style'},
                {'value': 'minimal', 'label': 'Minimal'},
                {'value': 'dark', 'label': 'Dark'}
            ],
            'features': [
                {'key': 'allow_signups', 'label': 'Allow Signups', 'type': 'toggle'}
            ]
        }
    
    def get_current_settings(self):
        """Get current settings"""
        settings = self.settings_service.get_settings()
        return {
            'theme': settings.get('theme', 'login-style'),
            'allow_signups': settings.get('allow_signups', False)
        }
    
    def validate_settings_update(self, user_role):
        """Validate if user can update settings"""
        allowed_roles = ['admin', 'super_admin']
        return user_role in allowed_roles, f"User role {user_role} cannot update settings"
    
    def validate_settings_view(self, user_role):
        """Validate if user can view settings"""
        allowed_roles = ['admin', 'super_admin']
        return user_role in allowed_roles, "Access denied to settings"
    
    def get_settings_permissions(self, user_role):
        """Get settings permissions based on role"""
        permissions = {
            'emp': {
                'can_view': False,
                'can_edit': False,
                'can_view_theme': False,
                'can_change_theme': False
            },
            'admin': {
                'can_view': True,
                'can_edit': True,
                'can_view_theme': True,
                'can_change_theme': True
            },
            'super_admin': {
                'can_view': True,
                'can_edit': True,
                'can_view_theme': True,
                'can_change_theme': True
            }
        }
        return permissions.get(user_role, {})
    
    def get_settings_metadata(self):
        """Get settings page metadata"""
        return {
            'page_title': '⚙️ Settings',
            'page_description': 'Manage application settings',
            'sections': [
                {'name': 'appearance', 'label': 'Appearance'},
                {'name': 'features', 'label': 'Features'}
            ]
        }


@settings_page_bp.route('/options', methods=['GET'])
def get_settings_options():
    """Get available settings options"""
    service = SettingsPageService()
    options = service.get_available_settings()
    
    return jsonify({
        'success': True,
        'options': options
    })


@settings_page_bp.route('/current', methods=['GET'])
@require_auth
def get_current_settings(**kwargs):
    """Get current settings"""
    current_user = kwargs.get('current_user')
    service = SettingsPageService()
    settings = service.get_current_settings()
    
    return jsonify({
        'success': True,
        'settings': settings
    })


@settings_page_bp.route('/can-edit', methods=['GET'])
@require_auth
def can_edit_settings(**kwargs):
    """Check if user can edit settings"""
    current_user = kwargs.get('current_user')
    service = SettingsPageService()
    can_edit, message = service.validate_settings_update(current_user['role'])
    
    return jsonify({
        'success': True,
        'can_edit': can_edit,
        'user_role': current_user['role'],
        'message': message if not can_edit else 'You can update settings'
    })


@settings_page_bp.route('/metadata', methods=['GET'])
def get_settings_metadata():
    """Get settings page metadata"""
    service = SettingsPageService()
    metadata = service.get_settings_metadata()
    
    return jsonify({
        'success': True,
        'metadata': metadata
    })


@settings_page_bp.route('/permissions', methods=['GET'])
@require_auth
def get_settings_permissions(**kwargs):
    """Get settings permissions for current user"""
    current_user = kwargs.get('current_user')
    service = SettingsPageService()
    permissions = service.get_settings_permissions(current_user['role'])
    
    return jsonify({
        'success': True,
        'role': current_user['role'],
        'permissions': permissions
    })


@settings_page_bp.route('/')
def settings_page():
    """Render settings page"""
    return render_template('settings.html')
