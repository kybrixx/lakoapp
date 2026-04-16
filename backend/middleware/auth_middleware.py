from functools import wraps
from flask import request, jsonify
from auth import Auth

class AuthMiddleware:
    @staticmethod
    def require_auth(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.headers.get('X-Session-Token')
            if not token:
                return jsonify({'error': 'Missing session token'}), 401
            user = Auth.get_user_by_token(token)
            if not user:
                return jsonify({'error': 'Invalid session token'}), 401
            if user.get('is_suspended'):
                return jsonify({'error': 'Account suspended'}), 403
            request.user = user
            return f(*args, **kwargs)
        return decorated
    
    @staticmethod
    def require_role(roles):
        def decorator(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                token = request.headers.get('X-Session-Token')
                if not token:
                    return jsonify({'error': 'Missing session token'}), 401
                user = Auth.get_user_by_token(token)
                if not user:
                    return jsonify({'error': 'Invalid session token'}), 401
                if user.get('is_suspended'):
                    return jsonify({'error': 'Account suspended'}), 403
                if user.get('role') not in roles:
                    return jsonify({'error': 'Insufficient permissions'}), 403
                request.user = user
                return f(*args, **kwargs)
            return decorated
        return decorator

require_auth = AuthMiddleware.require_auth
require_role = AuthMiddleware.require_role
