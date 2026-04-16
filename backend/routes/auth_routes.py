from flask import Blueprint, request, jsonify
from auth import Auth
from database import db
from utils import validate_email, validate_phone

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register/customer', methods=['POST'])
def register_customer():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')
    phone = data.get('phone')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    if not validate_email(email):
        return jsonify({'error': 'Invalid email format'}), 400
    
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    result = Auth.register_user(email, password, 'customer', full_name, phone)
    
    if result['success']:
        db.log_activity(result['user']['id'], 'customer', 'register', details='Customer registration')
        return jsonify({
            'session_token': result['session_token'],
            'user': {
                'id': result['user']['id'],
                'email': result['user']['email'],
                'role': result['user']['role'],
                'full_name': result['user']['full_name']
            }
        }), 201
    
    return jsonify({'error': result['error']}), 400

@auth_bp.route('/register/vendor', methods=['POST'])
def register_vendor():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    business_name = data.get('business_name')
    category = data.get('category')
    address = data.get('address')
    phone = data.get('phone')
    description = data.get('description')
    lat = data.get('latitude')
    lng = data.get('longitude')
    
    if not all([email, password, business_name, category, address]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if not validate_email(email):
        return jsonify({'error': 'Invalid email format'}), 400
    
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    result = Auth.register_user(email, password, 'vendor', business_name, phone, address)
    
    if result['success']:
        user_id = result['user']['id']
        vendor_id = db.create_vendor(user_id, business_name, category, address, lat, lng, phone, email, description)
        db.log_activity(user_id, 'vendor', 'register', details='Vendor registration')
        return jsonify({
            'session_token': result['session_token'],
            'user': {
                'id': user_id,
                'email': email,
                'role': 'vendor',
                'full_name': business_name
            },
            'vendor_id': vendor_id
        }), 201
    
    return jsonify({'error': result['error']}), 400

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    result = Auth.login(email, password)
    
    if result['success']:
        user = result['user']
        response = {
            'session_token': result['session_token'],
            'user': {
                'id': user['id'],
                'email': user['email'],
                'role': user['role'],
                'full_name': user['full_name'],
                'avatar': user.get('avatar')
            }
        }
        
        if user['role'] == 'vendor':
            vendor = db.get_vendor_by_user_id(user['id'])
            if vendor:
                response['vendor'] = {
                    'id': vendor['id'],
                    'business_name': vendor['business_name'],
                    'category': vendor['category'],
                    'is_active': vendor['is_active']
                }
        
        return jsonify(response), 200
    
    return jsonify({'error': result['error']}), 401

@auth_bp.route('/logout', methods=['POST'])
def logout():
    token = request.headers.get('X-Session-Token')
    user = Auth.get_user_by_token(token)
    if user:
        db.log_activity(user['id'], user['role'], 'logout')
    return jsonify({'success': True}), 200

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    token = request.headers.get('X-Session-Token')
    user = Auth.get_user_by_token(token)
    
    if not user:
        return jsonify({'error': 'Invalid session'}), 401
    
    return jsonify({
        'id': user['id'],
        'email': user['email'],
        'role': user['role'],
        'full_name': user['full_name'],
        'phone': user.get('phone'),
        'address': user.get('address'),
        'avatar': user.get('avatar'),
        'latitude': user.get('latitude'),
        'longitude': user.get('longitude')
    }), 200

@auth_bp.route('/update-location', methods=['POST'])
def update_location():
    token = request.headers.get('X-Session-Token')
    user = Auth.get_user_by_token(token)
    
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    lat = data.get('latitude')
    lng = data.get('longitude')
    
    if lat is None or lng is None:
        return jsonify({'error': 'Latitude and longitude required'}), 400
    
    db.update_user_location(user['id'], lat, lng)
    
    if user['role'] == 'vendor':
        vendor = db.get_vendor_by_user_id(user['id'])
        if vendor:
            db.update_vendor_location(vendor['id'], lat, lng)
    
    return jsonify({'success': True}), 200

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'Email required'}), 400
    
    user = db.get_user_by_email(email)
    if not user:
        return jsonify({'error': 'Email not found'}), 404
    
    # TODO: Send reset email
    return jsonify({'message': 'Password reset email sent'}), 200