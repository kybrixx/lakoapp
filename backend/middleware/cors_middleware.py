from flask import request, jsonify

class CORSMiddleware:
    @staticmethod
    def add_cors_headers(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-Session-Token'
        return response
    @staticmethod
    def register(app):
        app.after_request(CORSMiddleware.add_cors_headers)
