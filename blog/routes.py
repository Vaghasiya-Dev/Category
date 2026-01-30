from flask import Blueprint, request, jsonify
from auth.decorators import require_auth, require_role
from blog.services import BlogService

blog_bp = Blueprint('blog', __name__, url_prefix='/api/blog')


def get_service():
    return BlogService()


@blog_bp.route('/', methods=['GET'])
@require_auth
def get_blog(**kwargs):
    current_user = kwargs.get('current_user')
    service = get_service()
    return jsonify({
        'success': True,
        'data': service.get_blog()
    })


@blog_bp.route('/', methods=['PUT'])
@require_auth
@require_role('admin', 'super_admin')
def update_blog(**kwargs):
    current_user = kwargs.get('current_user')
    service = get_service()
    data = request.get_json() or {}
    updated = service.update_blog(data)
    return jsonify({
        'success': True,
        'data': updated
    })
