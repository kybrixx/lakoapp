import re
import uuid
import bcrypt
from datetime import datetime, timedelta
from database import db

class AuthService:
    @staticmethod
    def validate_email(email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password(password):
        if len(password) < 6:
            return False, "Password must be at least 6 characters"
        return True, None
    
    @staticmethod
    def validate_phone(phone):
        if not phone:
            return True, None
        pattern = r'^[\d\s\+\-\(\)]{10,15}$'
        if not re.match(pattern, phone):
            return False, "Invalid phone number format"
        return True, None
    
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
    def register(email, password, role, **kwargs):
        # Validate email
        if not AuthService.validate_email(email):
            return {'success': False, 'error': 'Invalid email format'}
        
        # Validate password
        valid, error = AuthService.validate_password(password)
        if not valid:
            return {'success': False, 'error': error}
        
        # Validate phone if provided
        phone = kwargs.get('phone')
        valid, error = AuthService.validate_phone(phone)
        if not valid:
            return {'success': False, 'error': error}
        
        # Check existing user
        existing = db.get_user_by_email(email)
        if existing:
            return {'success': False, 'error': 'Email already registered'}
        
        # Create user
        try:
            user_id = db.create_user(
                email=email,
                password=password,
                role=role,
                full_name=kwargs.get('full_name'),
                phone=kwargs.get('phone'),
                address=kwargs.get('address')
            )
            user = db.get_user_by_id(user_id)
            
            db.log_activity(user_id, role, 'register', details=f"{role} registration")
            
            return {
                'success': True,
                'user': user,
                'session_token': user_id
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def login(email, password):
        user = db.get_user_by_email(email)
        if not user:
            return {'success': False, 'error': 'Invalid email or password'}
        
        if not AuthService.verify_password(password, user['password']):
            return {'success': False, 'error': 'Invalid email or password'}
        
        if user.get('is_suspended'):
            suspension_until = user.get('suspension_until')
            if suspension_until:
                try:
                    until = datetime.fromisoformat(suspension_until)
                    if until > datetime.now():
                        return {'success': False, 'error': f'Account suspended until {suspension_until}'}
                    else:
                        db.unsuspend_user(user['id'])
                except:
                    pass
            else:
                return {'success': False, 'error': 'Account permanently suspended'}
        
        db.log_activity(user['id'], user['role'], 'login', details='User logged in')
        
        return {
            'success': True,
            'user': user,
            'session_token': user['id']
        }
    
    @staticmethod
    def logout(user_id):
        user = db.get_user_by_id(user_id)
        if user:
            db.log_activity(user_id, user['role'], 'logout')
        return {'success': True}
    
    @staticmethod
    def get_user_by_token(token):
        if not token:
            return None
        return db.get_user_by_id(token)
    
    @staticmethod
    def check_suspension(user_id):
        user = db.get_user_by_id(user_id)
        if not user:
            return {'suspended': False}
        
        if user.get('is_suspended'):
            suspension_until = user.get('suspension_until')
            if suspension_until:
                try:
                    until = datetime.fromisoformat(suspension_until)
                    if until > datetime.now():
                        return {
                            'suspended': True,
                            'until': suspension_until,
                            'reason': user.get('suspension_reason')
                        }
                    else:
                        db.unsuspend_user(user_id)
                except:
                    pass
            else:
                return {
                    'suspended': True,
                    'permanent': True,
                    'reason': user.get('suspension_reason')
                }
        
        return {'suspended': False}
    
    @staticmethod
    def authorize(token, allowed_roles=None):
        if not token:
            return {'authorized': False, 'error': 'Missing session token'}
        
        user = db.get_user_by_id(token)
        if not user:
            return {'authorized': False, 'error': 'Invalid session'}
        
        suspension = AuthService.check_suspension(user['id'])
        if suspension['suspended']:
            return {'authorized': False, 'error': 'Account suspended', 'suspension': suspension}
        
        if allowed_roles and user['role'] not in allowed_roles:
            return {'authorized': False, 'error': 'Insufficient permissions'}
        
        return {'authorized': True, 'user': user}
    
    @staticmethod
    def update_profile(user_id, data):
        conn = db.get_connection()
        c = conn.cursor()
        
        allowed_fields = ['full_name', 'phone', 'address', 'bio', 'avatar']
        updates = []
        values = []
        
        for field in allowed_fields:
            if field in data:
                updates.append(f"{field} = ?")
                values.append(data[field])
        
        if updates:
            values.append(user_id)
            c.execute(f"UPDATE users SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", values)
            conn.commit()
        
        conn.close()
        return {'success': True}
    
    @staticmethod
    def change_password(user_id, current_password, new_password):
        user = db.get_user_by_id(user_id)
        if not user:
            return {'success': False, 'error': 'User not found'}
        
        if not AuthService.verify_password(current_password, user['password']):
            return {'success': False, 'error': 'Current password is incorrect'}
        
        valid, error = AuthService.validate_password(new_password)
        if not valid:
            return {'success': False, 'error': error}
        
        hashed = AuthService.hash_password(new_password)
        conn = db.get_connection()
        c = conn.cursor()
        c.execute('UPDATE users SET password = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?', (hashed, user_id))
        conn.commit()
        conn.close()
        
        return {'success': True}
    
    @staticmethod
    def reset_password_request(email):
        user = db.get_user_by_email(email)
        if not user:
            return {'success': False, 'error': 'Email not found'}
        
        # Generate reset token (simplified - in production use JWT or separate table)
        reset_token = str(uuid.uuid4())
        
        # TODO: Send email with reset link
        # For now, just return token
        
        return {'success': True, 'reset_token': reset_token}
    
    @staticmethod
    def reset_password_confirm(token, new_password):
        # TODO: Verify token and update password
        valid, error = AuthService.validate_password(new_password)
        if not valid:
            return {'success': False, 'error': error}
        
        return {'success': True}