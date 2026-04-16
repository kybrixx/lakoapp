from flask import request, jsonify
from datetime import datetime, timedelta
from collections import defaultdict

class RateLimiter:
    _requests = defaultdict(list)
    @staticmethod
    def rate_limit(max_requests=60, window_seconds=60):
        def decorator(f):
            def decorated(*args, **kwargs):
                ip = request.remote_addr or 'unknown'
                now = datetime.now()
                window_start = now - timedelta(seconds=window_seconds)
                RateLimiter._requests[ip] = [t for t in RateLimiter._requests[ip] if t > window_start]
                if len(RateLimiter._requests[ip]) >= max_requests:
                    return jsonify({'error': 'Rate limit exceeded'}), 429
                RateLimiter._requests[ip].append(now)
                return f(*args, **kwargs)
            decorated.__name__ = f.__name__
            return decorated
        return decorator

rate_limit = RateLimiter.rate_limit
