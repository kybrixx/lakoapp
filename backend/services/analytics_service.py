from datetime import datetime, timedelta
from database import db

class AnalyticsService:
    @staticmethod
    def get_platform_stats():
        return db.get_stats()
    
    @staticmethod
    def get_vendor_analytics(vendor_id):
        vendor = db.get_vendor_by_id(vendor_id)
        if not vendor:
            return {'error': 'Vendor not found'}
        
        products = db.get_products_by_vendor(vendor_id)
        reviews = db.get_reviews_by_vendor(vendor_id)
        
        # Product performance
        product_stats = []
        for p in products:
            product_stats.append({
                'id': p['id'],
                'name': p['name'],
                'views': p.get('views', 0),
                'reviews': p.get('review_count', 0),
                'rating': p.get('rating', 0)
            })
        
        product_stats.sort(key=lambda x: x['reviews'], reverse=True)
        
        return {
            'vendor': {
                'name': vendor['business_name'],
                'total_views': vendor.get('traffic_count', 0),
                'total_reviews': len(reviews),
                'average_rating': vendor.get('rating', 0)
            },
            'top_products': product_stats[:5],
            'review_distribution': AnalyticsService.get_rating_distribution(vendor_id)
        }
    
    @staticmethod
    def get_rating_distribution(vendor_id):
        conn = db.get_connection()
        c = conn.cursor()
        c.execute('''SELECT rating, COUNT(*) as count FROM reviews 
                     WHERE vendor_id = ? GROUP BY rating''', (vendor_id,))
        
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for row in c.fetchall():
            distribution[row[0]] = row[1]
        
        conn.close()
        return distribution
    
    @staticmethod
    def get_user_analytics(user_id):
        conn = db.get_connection()
        c = conn.cursor()
        
        # Reviews written
        c.execute('SELECT COUNT(*) FROM reviews WHERE customer_id = ?', (user_id,))
        reviews_count = c.fetchone()[0]
        
        # Posts created
        c.execute('SELECT COUNT(*) FROM posts WHERE user_id = ?', (user_id,))
        posts_count = c.fetchone()[0]
        
        # Likes given
        c.execute('SELECT COUNT(*) FROM post_likes WHERE user_id = ?', (user_id,))
        likes_given = c.fetchone()[0]
        
        # Vendors shortlisted
        c.execute('SELECT COUNT(*) FROM shortlists WHERE user_id = ?', (user_id,))
        shortlisted = c.fetchone()[0]
        
        conn.close()
        
        return {
            'reviews_written': reviews_count,
            'posts_created': posts_count,
            'likes_given': likes_given,
            'vendors_shortlisted': shortlisted
        }
    
    @staticmethod
    def get_admin_analytics():
        stats = db.get_stats()
        
        # Get user growth (last 7 days)
        conn = db.get_connection()
        c = conn.cursor()
        
        seven_days_ago = datetime.now() - timedelta(days=7)
        c.execute('''SELECT DATE(created_at) as date, COUNT(*) as count 
                     FROM users WHERE created_at >= ? 
                     GROUP BY DATE(created_at) ORDER BY date''', (seven_days_ago,))
        
        user_growth = [{'date': row[0], 'count': row[1]} for row in c.fetchall()]
        
        # Active users today
        today = datetime.now().date()
        c.execute('''SELECT COUNT(DISTINCT user_id) FROM activities 
                     WHERE DATE(created_at) = ?''', (today,))
        active_today = c.fetchone()[0]
        
        conn.close()
        
        return {
            'total_stats': stats,
            'user_growth': user_growth,
            'active_today': active_today
        }