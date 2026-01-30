from flask import Blueprint, request, jsonify
from auth.decorators import require_auth, require_role
from settings.services import SettingsService

settings_bp = Blueprint('settings', __name__, url_prefix='/api/settings')


def get_service():
    return SettingsService()


@settings_bp.route('/', methods=['GET'])
@require_auth
def get_settings(**kwargs):
    current_user = kwargs.get('current_user')
    service = get_service()
    return jsonify({
        'success': True,
        'data': service.get_settings()
    })


@settings_bp.route('/', methods=['PUT'])
@require_auth
@require_role('admin', 'super_admin')
def update_settings(**kwargs):
    current_user = kwargs.get('current_user')
    service = get_service()
    data = request.get_json() or {}
    updated = service.update_settings(data)
    return jsonify({
        'success': True,
        'data': updated
    })
