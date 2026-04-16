import uuid
import bcrypt
from datetime import datetime
from database import db

class Auth:
    @staticmethod
    def hash_password(password):
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    
    @staticmethod
    def verify_password(password, hashed):
        return bcrypt.checkpw(password.encode(), hashed.encode())
    
    @staticmethod
    def generate_token():
        return str(uuid.uuid4())
    
    @staticmethod
    def register_user(email, password, role, full_name=None, phone=None, address=None):
        existing = db.get_user_by_email(email)
        if existing:
            return {'success': False, 'error': 'Email already registered'}
        user_id = db.create_user(email, password, role, full_name, phone, address)
        user = db.get_user_by_id(user_id)
        return {'success': True, 'user': user, 'session_token': user_id}
    
    @staticmethod
    def login(email, password):
        user = db.verify_password(email, password)
        if not user:
            return {'success': False, 'error': 'Invalid email or password'}
        if user.get('is_suspended'):
            return {'success': False, 'error': 'Account suspended'}
        db.log_activity(user['id'], user['role'], 'login', details=f"User logged in")
        return {'success': True, 'user': user, 'session_token': user['id']}
    
    @staticmethod
    def get_user_by_token(token):
        if not token:
            return None
        return db.get_user_by_id(token)
    
    @staticmethod
    def require_role(token, allowed_roles):
        user = Auth.get_user_by_token(token)
        if not user:
            return {'authorized': False, 'error': 'Authentication required'}
        if user['role'] not in allowed_roles:
            return {'authorized': False, 'error': 'Insufficient permissions'}
        if user.get('is_suspended'):
            return {'authorized': False, 'error': 'Account suspended'}
        return {'authorized': True, 'user': user}