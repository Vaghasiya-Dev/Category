"""
Categories Page Handler
Handles categories page rendering and category operations
"""
from flask import Blueprint, render_template, jsonify, current_app
from categories.services import CategoryService
from auth.decorators import require_auth, check_permission

categories_page_bp = Blueprint('categories_page', __name__, url_prefix='/categories-handler')


class CategoriesPageService:
    """Business logic for categories page"""
    
    def __init__(self):
        self.category_service = CategoryService()
    
    def get_categories_display(self):
        """Get categories for display"""
        categories = self.category_service.get_all_categories()
        return categories
    
    def get_category_tree_display(self):
        """Get category tree for display"""
        tree = self.category_service.get_category_tree()
        return tree
    
    def validate_category_edit(self, user_role):
        """Validate if user can edit categories"""
        allowed_roles = ['super_admin']
        can_edit = user_role in allowed_roles
        return can_edit, f"Only Super Admin can edit categories"
    
    def validate_category_view(self, user_role):
        """Validate if user can view categories"""
        allowed_roles = ['admin', 'super_admin', 'emp']
        can_view = user_role in allowed_roles
        return can_view, "Access denied"
    
    def get_categories_permissions(self, user_role):
        """Get categories permissions based on role"""
        permissions = {
            'emp': {
                'can_view': True,
                'can_edit': False,
                'can_add': False,
                'can_delete': False,
                'can_reorder': False
            },
            'admin': {
                'can_view': True,
                'can_edit': False,
                'can_add': False,
                'can_delete': False,
                'can_reorder': False
            },
            'super_admin': {
                'can_view': True,
                'can_edit': True,
                'can_add': True,
                'can_delete': True,
                'can_reorder': True
            }
        }
        return permissions.get(user_role, {})
    
    def get_categories_metadata(self):
        """Get categories page metadata"""
        return {
            'page_title': '📂 Categories',
            'page_description': 'Browse hierarchical categories',
            'tree_title': 'Category Tree',
            'readonly_message': 'You have view-only access to categories',
            'admin_only_message': 'Only Super Admin can manage categories'
        }


@categories_page_bp.route('/list', methods=['GET'])
@require_auth
def get_categories_list(**kwargs):
    """Get categories list"""
    current_user = kwargs.get('current_user')
    service = CategoriesPageService()
    can_view, msg = service.validate_category_view(current_user['role'])
    
    if not can_view:
        return jsonify({'success': False, 'message': msg}), 403
    
    categories = service.get_categories_display()
    return jsonify({
        'success': True,
        'categories': categories
    })


@categories_page_bp.route('/tree', methods=['GET'])
@require_auth
def get_categories_tree(**kwargs):
    """Get categories tree"""
    current_user = kwargs.get('current_user')
    service = CategoriesPageService()
    can_view, msg = service.validate_category_view(current_user['role'])
    
    if not can_view:
        return jsonify({'success': False, 'message': msg}), 403
    
    tree = service.get_category_tree_display()
    return jsonify({
        'success': True,
        'tree': tree
    })


@categories_page_bp.route('/can-edit', methods=['GET'])
@require_auth
def can_edit_categories(**kwargs):
    """Check if user can edit categories"""
    current_user = kwargs.get('current_user')
    service = CategoriesPageService()
    can_edit, message = service.validate_category_edit(current_user['role'])
    
    return jsonify({
        'success': True,
        'can_edit': can_edit,
        'user_role': current_user['role'],
        'message': message if not can_edit else 'You can manage categories'
    })


@categories_page_bp.route('/metadata', methods=['GET'])
def get_categories_metadata():
    """Get categories page metadata"""
    service = CategoriesPageService()
    metadata = service.get_categories_metadata()
    
    return jsonify({
        'success': True,
        'metadata': metadata
    })


@categories_page_bp.route('/permissions', methods=['GET'])
@require_auth
def get_categories_permissions(**kwargs):
    """Get categories permissions for current user"""
    current_user = kwargs.get('current_user')
    service = CategoriesPageService()
    permissions = service.get_categories_permissions(current_user['role'])
    
    return jsonify({
        'success': True,
        'role': current_user['role'],
        'permissions': permissions
    })


@categories_page_bp.route('/')
def categories_page():
    """Render categories page"""
    return render_template('categories.html')