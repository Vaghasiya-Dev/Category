from flask import Blueprint, request, jsonify
from categories.services import CategoryService
from auth.decorators import require_auth, check_permission
 
categories_bp = Blueprint('categories', __name__, url_prefix='/api/categories')

# Remove this line: service = CategoryService()
# Create service in each route function instead

def get_service():
    """Helper function to get CategoryService instance"""
    return CategoryService()
 
 
@categories_bp.route('/', methods=['GET'])
@require_auth
def get_all_categories(**kwargs):
    """Get all categories (all roles can access)"""
    current_user = kwargs.get('current_user')
    service = get_service()
    categories = service.get_all_categories()
    
    return jsonify({
        'success': True,
        'categories': categories
    })
 
 
@categories_bp.route('/tree', methods=['GET'])
@require_auth
def get_category_tree(**kwargs):
    """Get category tree with metadata"""
    current_user = kwargs.get('current_user')
    service = get_service()
    tree = service.get_category_tree()
    
    return jsonify({
        'success': True,
        'tree': tree
    })
 
 
@categories_bp.route('/', methods=['POST'])
@require_auth
@check_permission('can_manage_categories')
def create_category(**kwargs):
    """
    Create new category (Super Admin only)
    
    Request Body:
        {
            "parent_path": ["Electronics", "Audio Device"],  // Optional, empty for root level
            "category_name": "New Category"
        }
    """
    current_user = kwargs.get('current_user')
    service = get_service()
    data = request.get_json()
    
    if not data or 'category_name' not in data:
        return jsonify({
            'success': False,
            'message': 'Missing required field: category_name'
        }), 400
    
    if not data['category_name'] or data['category_name'].strip() == '':
        return jsonify({
            'success': False,
            'message': 'Category name cannot be empty'
        }), 400
    
    parent_path = data.get('parent_path', [])
    if not isinstance(parent_path, list):
        return jsonify({
            'success': False,
            'message': 'parent_path must be an array'
        }), 400
    
    success, message = service.add_category(
        parent_path=parent_path,
        new_category_name=data['category_name'].strip()
    )
    
    if not success:
        return jsonify({
            'success': False,
            'message': message
        }), 400
    
    return jsonify({
        'success': True,
        'message': message
    }), 201
 
 
@categories_bp.route('/update', methods=['PUT'])
@require_auth
@check_permission('can_manage_categories')
def update_category(**kwargs):
    """
    Update category (Super Admin only)
    
    Request Body:
        {
            "category_path": ["Electronics", "Audio Device", "Headphones"],
            "new_name": "Updated Headphones"
        }
    """
    current_user = kwargs.get('current_user')
    service = get_service()
    data = request.get_json()
    
    if not data or 'category_path' not in data or 'new_name' not in data:
        return jsonify({
            'success': False,
            'message': 'Missing required fields: category_path, new_name'
        }), 400
    
    if not data['new_name'] or data['new_name'].strip() == '':
        return jsonify({
            'success': False,
            'message': 'New name cannot be empty'
        }), 400
    
    success, message = service.update_category(
        old_path=data['category_path'],
        new_name=data['new_name'].strip()
    )
    
    if not success:
        return jsonify({
            'success': False,
            'message': message
        }), 400
    
    return jsonify({
        'success': True,
        'message': message
    })
 
 
@categories_bp.route('/delete', methods=['DELETE'])
@require_auth
@check_permission('can_manage_categories')
def delete_category(**kwargs):
    """
    Delete category (Super Admin only)
    
    Request Body:
        {
            "category_path": ["Electronics", "Audio Device", "Headphones"]
        }
    """
    current_user = kwargs.get('current_user')
    service = get_service()
    data = request.get_json()
    
    if not data or 'category_path' not in data:
        return jsonify({
            'success': False,
            'message': 'Missing required field: category_path'
        }), 400
    
    success, message = service.delete_category(
        category_path=data['category_path']
    )
    
    if not success:
        return jsonify({
            'success': False,
            'message': message
        }), 400
    
    return jsonify({
        'success': True,
        'message': message
    })  