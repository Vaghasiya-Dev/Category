from flask import Blueprint, request, jsonify
from audiences.services import AudienceService
from auth.decorators import require_auth, check_permission, require_role
import logging

# Configure logging for Vercel
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
 
audiences_bp = Blueprint('audiences', __name__, url_prefix='/api/audiences')

# Remove this line: service = AudienceService()
# Create service in each route function instead

def get_service():
    """Helper function to get AudienceService instance"""
    try:
        return AudienceService()
    except Exception as e:
        logger.error(f"Error creating AudienceService: {e}")
        raise
 
 
@audiences_bp.route('/', methods=['POST'])
@require_auth
@check_permission('can_manage_audiences')
def add_audience(**kwargs):
    """
    Add audience to category (Admin and Super Admin)
    
    Request Body:
        {
            "audience_id": "string",
            "category_path": ["Electronics", "Audio Device", "Headphones"],
            "audience_info": {
                "names": ["cardio", "fitness"],
                "min_age": 18,
                "max_age": 65
            }
        }
    """
    current_user = kwargs.get('current_user')
    try:
        service = get_service()
        data = request.get_json()
        
        # Log request for debugging on Vercel
        logger.info(f"Add audience request: {data}")
        
        if not data or 'audience_id' not in data or 'category_path' not in data:
            logger.warning("Missing required fields in request")
            return jsonify({
                'success': False,
                'message': 'Missing required fields: audience_id, category_path'
            }), 400
        
        if not isinstance(data['category_path'], list):
            return jsonify({
                'success': False,
                'message': 'category_path must be an array'
            }), 400
        
        if not data['category_path']:
            return jsonify({
                'success': False,
                'message': 'category_path cannot be empty'
            }), 400
        
        result = service.add_audience_to_leaf_node(
            audience_id=data['audience_id'],
            category_path=data['category_path'],
            audience_info=data.get('audience_info'),
            created_by=current_user['user_id']
        )
        
        if result['success']:
            logger.info(f"Successfully added audience: {data['audience_id']}")
            return jsonify(result), 201
        logger.error(f"Failed to add audience: {result.get('message')}")
        return jsonify(result), 500
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Exception in add_audience: {error_trace}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error': str(e)
        }), 500
 
 
@audiences_bp.route('/batch', methods=['POST'])
@require_auth
@check_permission('can_manage_audiences')
def batch_add_audiences(**kwargs):
    """
    Batch add audiences to category
    
    Request Body:
        {
            "audience_ids": ["aud1", "aud2", "aud3"],
            "category_path": ["Electronics", "Audio Device", "Headphones"]
        }
    """
    current_user = kwargs.get('current_user')
    service = get_service()
    data = request.get_json()
    
    if not data or 'audience_ids' not in data or 'category_path' not in data:
        return jsonify({
            'success': False,
            'message': 'Missing required fields: audience_ids, category_path'
        }), 400
    
    if not isinstance(data['audience_ids'], list):
        return jsonify({
            'success': False,
            'message': 'audience_ids must be an array'
        }), 400
    
    if not data['audience_ids']:
        return jsonify({
            'success': False,
            'message': 'audience_ids cannot be empty'
        }), 400
    
    result = service.batch_add_audience_to_category(
        audience_ids=data['audience_ids'],
        category_path=data['category_path'],
        created_by=current_user['user_id']
    )
    
    return jsonify(result)
 
 
@audiences_bp.route('/categories/<path:category_path>/audiences', methods=['GET'])
@require_auth
def get_category_audiences(category_path, **kwargs):
    """
    Get all audiences assigned to a specific category
    
    Path: /api/audiences/categories/Electronics/Audio%20Device/Headphones/audiences
    """
    current_user = kwargs.get('current_user')
    try:
        service = get_service()
        path_list = category_path.split('/')
        logger.info(f"Fetching audiences for category path: {path_list}")
        audiences = service.get_category_audiences(path_list)
        logger.info(f"Found {len(audiences)} audiences for category: {path_list}")
        
        return jsonify({
            'success': True,
            'category_path': path_list,
            'audiences': audiences,
            'count': len(audiences)
        })
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Exception in get_category_audiences: {error_trace}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error': str(e)
        }), 500


@audiences_bp.route('/categories/<path:category_path>/has-audience', methods=['GET'])
@require_auth
def check_category_has_audience(category_path, **kwargs):
    """
    Check if a category already has an audience assigned
    
    Returns:
        {
            'success': bool,
            'has_audience': bool,
            'audience_id': str (if has_audience is True),
            'audience_info': dict (if has_audience is True)
        }
    
    Path: /api/audiences/categories/Electronics/Audio%20Device/Headphones/has-audience
    """
    current_user = kwargs.get('current_user')
    service = get_service()
    path_list = category_path.split('/')
    audiences = service.get_category_audiences(path_list)
    
    # Ensure only one audience per category - return first one if exists
    has_audience = len(audiences) > 0
    audience_data = audiences[0] if audiences else None
    
    return jsonify({
        'success': True,
        'category_path': path_list,
        'has_audience': has_audience,
        'audience_id': audience_data['audience_id'] if audience_data else None,
        'audience_info': audience_data['audience_info'] if audience_data else None
    })
 
 
@audiences_bp.route('/<audience_id>/categories', methods=['GET'])
@require_auth
def get_audience_categories(audience_id, **kwargs):
    """
    Get all categories assigned to an audience
    
    Path: /api/audiences/aud001/categories
    """
    current_user = kwargs.get('current_user')
    service = get_service()
    categories = service.get_audience_categories(audience_id)
    
    return jsonify({
        'success': True,
        'audience_id': audience_id,
        'categories': categories,
        'count': len(categories)
    })
 
 
@audiences_bp.route('/<audience_id>', methods=['GET'])
@require_auth
def get_audience(audience_id, **kwargs):
    """
    Get audience by ID
    
    Path: /api/audiences/aud001
    """
    current_user = kwargs.get('current_user')
    service = get_service()
    audience = service.get_audience_by_id(audience_id)
    
    if not audience:
        return jsonify({
            'success': False,
            'message': 'Audience not found'
        }), 404
    
    return jsonify({
        'success': True,
        'audience': audience
    })
 
 
@audiences_bp.route('/', methods=['GET'])
@require_auth
@require_role('admin', 'super_admin')
def get_all_audiences(**kwargs):
    """
    Get all audiences (Admin and Super Admin)
    
    Query Params:
        search: Search term (optional)
        limit: Number of results (optional, default: 50)
        offset: Pagination offset (optional, default: 0)
    """
    current_user = kwargs.get('current_user')
    try:
        service = get_service()
        logger.info("Fetching all audiences")
        audiences = service.get_all_audiences()
        logger.info(f"Found {len(audiences)} total audiences")
        
        # Apply search filter
        search = request.args.get('search', '').lower()
        if search:
            audiences = [
                a for a in audiences 
                if search in a.get('audience_id', '').lower() or 
                   any(search in cat.get('category_path_str', '').lower() for cat in a.get('categories', []))
            ]
        
        # Apply pagination
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        paginated_audiences = audiences[offset:offset + limit]
        
        return jsonify({
            'success': True,
            'audiences': paginated_audiences,
            'total': len(audiences),
            'limit': limit,
            'offset': offset
        })
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Exception in get_all_audiences: {error_trace}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error': str(e)
        }), 500
 
 
@audiences_bp.route('/<audience_id>/category/<path:category_path>', methods=['DELETE'])
@require_auth
@check_permission('can_manage_audiences')
def remove_audience_from_category(audience_id, category_path, **kwargs):
    """
    Remove audience from specific category
    
    Path: /api/audiences/aud001/category/Electronics/Audio%20Device/Headphones
    """
    current_user = kwargs.get('current_user')
    service = get_service()
    path_list = category_path.split('/')
    
    result = service.remove_audience_from_category(
        audience_id=audience_id,
        category_path=path_list
    )
    
    if not result['success']:
        return jsonify(result), 400
    
    return jsonify(result)
 
 
@audiences_bp.route('/<audience_id>', methods=['PUT'])
@require_auth
@check_permission('can_manage_audiences')
def update_audience(audience_id, **kwargs):
    """
    Update audience information (Admin and Super Admin)
    Only updates existing fields in audience_info, does not create new nested objects
    
    Request Body:
        {
            "audience_info": {
                "names": ["cardio", "fitness"],
                "min_age": 18,
                "max_age": 65,
                "description": "Updated description",
                "target_criteria": "age:25-40"
            }
        }
    """
    current_user = kwargs.get('current_user')
    service = get_service()
    data = request.get_json()
    
    if not data or 'audience_info' not in data:
        return jsonify({
            'success': False,
            'message': 'Missing required field: audience_info'
        }), 400
    
    result = service.update_audience_info(
        audience_id=audience_id,
        audience_info=data['audience_info']
    )
    
    if not result['success']:
        return jsonify(result), 400
    
    return jsonify(result)


@audiences_bp.route('/statistics', methods=['GET'])
@require_auth
@require_role('admin', 'super_admin')
def get_statistics(**kwargs):
    """Get audience statistics (Admin and Super Admin)"""
    current_user = kwargs.get('current_user')
    service = get_service()
    stats = service.get_statistics()
    
    return jsonify({
        'success': True,
        'statistics': stats
    })