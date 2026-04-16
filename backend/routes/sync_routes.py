from flask import Blueprint, request, jsonify
from auth import Auth
from sync_service import SyncService

sync_bp = Blueprint('sync', __name__)

@sync_bp.before_request
def check_auth():
    token = request.headers.get('X-Session-Token')
    user = Auth.get_user_by_token(token)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    request.user = user

@sync_bp.route('/pull', methods=['GET'])
def pull_changes():
    tables = request.args.get('tables', '').split(',') if request.args.get('tables') else None
    changes = SyncService.pull_changes(request.user['id'], tables)
    return jsonify({'changes': changes, 'timestamp': request.user.get('last_sync')}), 200

@sync_bp.route('/push', methods=['POST'])
def push_changes():
    data = request.get_json()
    changes = data.get('changes', [])
    
    if not changes:
        return jsonify({'synced': [], 'message': 'No changes to sync'}), 200
    
    results = SyncService.push_changes(request.user['id'], changes)
    return jsonify({'results': results}), 200

@sync_bp.route('/status', methods=['GET'])
def get_sync_status():
    status = SyncService.get_sync_status(request.user['id'])
    return jsonify({'status': status}), 200

@sync_bp.route('/conflict', methods=['POST'])
def resolve_conflict():
    data = request.get_json()
    table = data.get('table')
    local = data.get('local')
    remote = data.get('remote')
    resolution = data.get('resolution')
    
    if resolution == 'local':
        return jsonify({'resolved': True, 'data': local}), 200
    elif resolution == 'remote':
        return jsonify({'resolved': True, 'data': remote}), 200
    elif resolution == 'merge':
        merged = {**remote, **local}
        return jsonify({'resolved': True, 'data': merged}), 200
    
    return jsonify({'error': 'Invalid resolution strategy'}), 400