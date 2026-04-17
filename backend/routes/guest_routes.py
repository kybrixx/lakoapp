from flask import Blueprint, request, jsonify
from database import db
from services.map_service import MapService

guest_bp = Blueprint('guest', __name__)

@guest_bp.route('/vendors', methods=['GET'])
def get_vendors():
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    radius = request.args.get('radius', 10, type=float)
    category = request.args.get('category')
    
    vendors = MapService.get_nearby_vendors(lat, lng, radius, category)
    return jsonify({'vendors': vendors}), 200

@guest_bp.route('/vendors/<vendor_id>', methods=['GET'])
def get_vendor(vendor_id):
    vendor = db.get_vendor_by_id(vendor_id)
    if not vendor:
        return jsonify({'error': 'Vendor not found'}), 404
    
    db.increment_traffic(vendor_id)
    db.log_traffic(vendor_id, None, None, None, 'guest_view')
    
    products = db.get_products_by_vendor(vendor_id)
    reviews = db.get_reviews_by_vendor(vendor_id)
    
    return jsonify({
        'vendor': vendor,
        'products': products,
        'reviews': reviews
    }), 200

@guest_bp.route('/products/<product_id>', methods=['GET'])
def get_product(product_id):
    product = db.get_product_by_id(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    reviews = db.get_reviews_by_product(product_id)
    
    return jsonify({
        'product': product,
        'reviews': reviews
    }), 200

@guest_bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    search_type = request.args.get('type', 'all')
    
    results = {}
    if search_type in ['all', 'vendors']:
        results['vendors'] = db.search_vendors(query)
    if search_type in ['all', 'products']:
        results['products'] = db.search_products(query)
    
    return jsonify(results), 200

@guest_bp.route('/heatmap', methods=['GET'])
def get_heatmap():
    data = MapService.get_heatmap_data()
    return jsonify({'points': data}), 200

@guest_bp.route('/map/config', methods=['GET'])
def get_map_config():
    return jsonify(MapService.get_map_config()), 200