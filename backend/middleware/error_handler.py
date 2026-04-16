from flask import jsonify
from config import config

class ErrorHandler:
    @staticmethod
    def handle_404(e):
        return jsonify({'error': 'Not found'}), 404
    @staticmethod
    def handle_500(e):
        if config.DEBUG:
            return jsonify({'error': str(e)}), 500
        return jsonify({'error': 'Internal server error'}), 500
    @staticmethod
    def register_handlers(app):
        app.register_error_handler(404, ErrorHandler.handle_404)
        app.register_error_handler(500, ErrorHandler.handle_500)

def handle_errors(app):
    ErrorHandler.register_handlers(app)
