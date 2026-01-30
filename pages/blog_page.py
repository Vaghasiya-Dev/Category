"""
Blog Page Handler
Handles blog page rendering and blog content operations
"""
from flask import Blueprint, render_template, jsonify, current_app
from blog.services import BlogService
from auth.decorators import require_auth

blog_page_bp = Blueprint('blog_page', __name__, url_prefix='/blog-handler')


class BlogPageService:
    """Business logic for blog page"""
    
    def __init__(self):
        self.blog_service = BlogService()
    
    def get_blog_content(self):
        """Get blog content for display"""
        content = self.blog_service.get_blog()
        return {
            'title': content.get('title', ''),
            'content': content.get('content', '')
        }
    
    def validate_blog_edit(self, user_role):
        """Validate if user can edit blog"""
        allowed_roles = ['admin', 'super_admin']
        return user_role in allowed_roles, f"User role {user_role} cannot edit blog"
    
    def validate_blog_view(self, user_role):
        """Validate if user can view blog"""
        allowed_roles = ['emp', 'admin', 'super_admin']
        return user_role in allowed_roles, "Access denied"
    
    def get_blog_permissions(self, user_role):
        """Get blog permissions based on role"""
        permissions = {
            'emp': {
                'can_view': True,
                'can_edit': False,
                'can_create': False,
                'can_delete': False
            },
            'admin': {
                'can_view': True,
                'can_edit': True,
                'can_create': True,
                'can_delete': True
            },
            'super_admin': {
                'can_view': True,
                'can_edit': True,
                'can_create': True,
                'can_delete': True
            }
        }
        return permissions.get(user_role, {})
    
    def get_blog_metadata(self):
        """Get blog page metadata"""
        return {
            'page_title': '📝 Blog',
            'page_description': 'Manage blog content',
            'readonly_message': 'You have read-only access to this page',
            'edit_disabled_message': 'Only admins and super admins can edit blog'
        }


@blog_page_bp.route('/content', methods=['GET'])
@require_auth
def get_blog_content(**kwargs):
    """Get blog content"""
    current_user = kwargs.get('current_user')
    service = BlogPageService()
    content = service.get_blog_content()
    
    return jsonify({
        'success': True,
        'data': content
    })


@blog_page_bp.route('/can-edit', methods=['GET'])
@require_auth
def can_edit_blog(**kwargs):
    """Check if user can edit blog"""
    current_user = kwargs.get('current_user')
    service = BlogPageService()
    can_edit, message = service.validate_blog_edit(current_user['role'])
    
    return jsonify({
        'success': True,
        'can_edit': can_edit,
        'user_role': current_user['role'],
        'message': message if not can_edit else 'You can edit'
    })


@blog_page_bp.route('/permissions', methods=['GET'])
@require_auth
def get_blog_permissions(**kwargs):
    """Get blog permissions for current user"""
    current_user = kwargs.get('current_user')
    service = BlogPageService()
    can_view, msg = service.validate_blog_view(current_user['role'])
    
    if not can_view:
        return jsonify({'success': False, 'message': msg}), 403
    
    permissions = service.get_blog_permissions(current_user['role'])
    
    return jsonify({
        'success': True,
        'permissions': permissions,
        'user_role': current_user['role']
    })


@blog_page_bp.route('/')
def blog_page():
    """Render blog page"""
    return render_template('blog.html')
