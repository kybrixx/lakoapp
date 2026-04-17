from flask import Blueprint, request, jsonify
from auth import Auth
from database import db
from services.map_service import MapService
from services.suggestion_service import SuggestionService

vendor_bp = Blueprint('vendor', __name__)

def get_vendor_id(user):
    vendor = db.get_vendor_by_user_id(user['id'])
    return vendor['id'] if vendor else None

@vendor_bp.route('/dashboard', methods=['GET'])
def get_dashboard():
    token = request.headers.get('X-Session-Token')
    auth = Auth.require_role(token, ['vendor'])
    
    if not auth['authorized']:
        return jsonify({'error': auth['error']}), 403
    
    user = auth['user']
    vendor = db.get_vendor_by_user_id(user['id'])
    
    if not vendor:
        return jsonify({'error': 'Vendor not found'}), 404
    
    products = db.get_products_by_vendor(vendor['id'])
    reviews = db.get_reviews_by_vendor(vendor['id'])
    
    stats = {
        'total_products': len(products),
        'total_reviews': len(reviews),
        'average_rating': vendor.get('rating', 0),
        'traffic_count': vendor.get('traffic_count', 0),
        'review_count': vendor.get('review_count', 0)
    }
    
    return jsonify({
        'vendor': vendor,
        'stats': stats,
        'recent_products': products[:5],
        'recent_reviews': reviews[:5]
    }), 200

@vendor_bp.route('/products', methods=['GET'])
def get_products():
    token = request.headers.get('X-Session-Token')
    auth = Auth.require_role(token, ['vendor'])
    
    if not auth['authorized']:
        return jsonify({'error': auth['error']}), 403
    
    vendor_id = get_vendor_id(auth['user'])
    if not vendor_id:
        return jsonify({'error': 'Vendor not found'}), 404
    
    products = db.get_products_by_vendor(vendor_id)
    return jsonify({'products': products}), 200

@vendor_bp.route('/products', methods=['POST'])
def create_product():
    token = request.headers.get('X-Session-Token')
    auth = Auth.require_role(token, ['vendor'])
    
    if not auth['authorized']:
        return jsonify({'error': auth['error']}), 403
    
    vendor_id = get_vendor_id(auth['user'])
    if not vendor_id:
        return jsonify({'error': 'Vendor not found'}), 404
    
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    category = data.get('category')
    price = data.get('price')
    moq = data.get('moq')
    stock = data.get('stock', 0)
    images = data.get('images')
    
    if not name:
        return jsonify({'error': 'Product name required'}), 400
    
    product_id = db.create_product(vendor_id, name, description, category, price, moq, stock, images)
    db.log_activity(auth['user']['id'], 'vendor', 'create_product', target_type='product', target_id=product_id)
    
    return jsonify({'id': product_id}), 201

@vendor_bp.route('/products/<product_id>', methods=['PUT'])
def update_product(product_id):
    token = request.headers.get('X-Session-Token')
    auth = Auth.require_role(token, ['vendor'])
    
    if not auth['authorized']:
        return jsonify({'error': auth['error']}), 403
    
    data = request.get_json()
    db.update_product(product_id, **data)
    
    return jsonify({'updated': True}), 200

@vendor_bp.route('/products/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    token = request.headers.get('X-Session-Token')
    auth = Auth.require_role(token, ['vendor'])
    
    if not auth['authorized']:
        return jsonify({'error': auth['error']}), 403
    
    db.delete_product(product_id)
    return jsonify({'deleted': True}), 200

@vendor_bp.route('/reviews', methods=['GET'])
def get_reviews():
    token = request.headers.get('X-Session-Token')
    auth = Auth.require_role(token, ['vendor'])
    
    if not auth['authorized']:
        return jsonify({'error': auth['error']}), 403
    
    vendor_id = get_vendor_id(auth['user'])
    if not vendor_id:
        return jsonify({'error': 'Vendor not found'}), 404
    
    reviews = db.get_reviews_by_vendor(vendor_id)
    return jsonify({'reviews': reviews}), 200

@vendor_bp.route('/traffic', methods=['GET'])
def get_traffic():
    token = request.headers.get('X-Session-Token')
    auth = Auth.require_role(token, ['vendor'])
    
    if not auth['authorized']:
        return jsonify({'error': auth['error']}), 403
    
    vendor_id = get_vendor_id(auth['user'])
    if not vendor_id:
        return jsonify({'error': 'Vendor not found'}), 404
    
    vendor = db.get_vendor_by_id(vendor_id)
    traffic_level = MapService.get_traffic_level(vendor_id)
    
    return jsonify({
        'traffic_count': vendor.get('traffic_count', 0),
        'traffic_level': traffic_level
    }), 200

@vendor_bp.route('/profile', methods=['PUT'])
def update_profile():
    token = request.headers.get('X-Session-Token')
    auth = Auth.require_role(token, ['vendor'])
    
    if not auth['authorized']:
        return jsonify({'error': auth['error']}), 403
    
    vendor_id = get_vendor_id(auth['user'])
    if not vendor_id:
        return jsonify({'error': 'Vendor not found'}), 404
    
    data = request.get_json()
    conn = db.get_connection()
    c = conn.cursor()
    
    fields = []
    values = []
    for k, v in data.items():
        if k in ['business_name', 'category', 'subcategory', 'description', 'address', 'phone', 'email', 'website', 'business_hours', 'logo', 'cover_image']:
            fields.append(f"{k} = ?")
            values.append(v)
    
    if fields:
        values.extend([vendor_id])
        c.execute(f"UPDATE vendors SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", values)
        conn.commit()
    
    conn.close()
    return jsonify({'updated': True}), 200

@vendor_bp.route('/analytics', methods=['GET'])
def get_analytics():
    token = request.headers.get('X-Session-Token')
    auth = Auth.require_role(token, ['vendor'])
    
    if not auth['authorized']:
        return jsonify({'error': auth['error']}), 403
    
    vendor_id = get_vendor_id(auth['user'])
    if not vendor_id:
        return jsonify({'error': 'Vendor not found'}), 404
    
    # Placeholder for detailed analytics
    vendor = db.get_vendor_by_id(vendor_id)
    products = db.get_products_by_vendor(vendor_id)
    reviews = db.get_reviews_by_vendor(vendor_id)
    
    return jsonify({
        'profile_views': vendor.get('traffic_count', 0),
        'total_products': len(products),
        'total_reviews': len(reviews),
        'average_rating': vendor.get('rating', 0),
        'top_products': sorted(products, key=lambda x: x.get('review_count', 0), reverse=True)[:5]
    }), 200

@vendor_bp.route('/suggestions', methods=['GET'])
def get_operation_suggestions():
    token = request.headers.get('X-Session-Token')
    auth = Auth.require_role(token, ['vendor'])
    
    if not auth['authorized']:
        return jsonify({'error': auth['error']}), 403
    
    vendor_id = get_vendor_id(auth['user'])
    if not vendor_id:
        return jsonify({'error': 'Vendor not found'}), 404
    
    suggestions = SuggestionService.get_vendor_operation_suggestions(vendor_id)
    return jsonify(suggestions), 200