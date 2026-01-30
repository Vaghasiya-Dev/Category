"""
Login Page Handler
Handles login page rendering and logic
"""
from flask import Blueprint, render_template, jsonify

login_bp = Blueprint('login', __name__, url_prefix='/login-handler')


class LoginService:
    """Business logic for login page"""
    
    @staticmethod
    def get_login_config():
        """Get configuration for login page"""
        return {
            'title': 'Login',
            'description': 'Role-based authentication system',
            'placeholder_username': 'Enter username',
            'placeholder_password': 'Enter password',
            'button_text': 'Sign In'
        }


@login_bp.route('/config', methods=['GET'])
def get_login_config():
    """Get login page configuration"""
    config = LoginService.get_login_config()
    return jsonify({
        'success': True,
        'config': config
    })


@login_bp.route('/')
def login_page():
    """Render login page"""
    return render_template('login.html')
