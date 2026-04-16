from flask import request, g
import time

class LoggingMiddleware:
    @staticmethod
    def log_request():
        g.start_time = time.time()
        print(f"[{request.method}] {request.path}")
    @staticmethod
    def log_response(response):
        if hasattr(g, 'start_time'):
            duration = (time.time() - g.start_time) * 1000
            print(f"[{response.status_code}] {duration:.2f}ms")
        return response
    @staticmethod
    def register(app):
        app.before_request(LoggingMiddleware.log_request)
        app.after_request(LoggingMiddleware.log_response)
