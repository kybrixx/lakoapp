from database import db
from datetime import datetime, timedelta
import json

class SuggestionService:
    @staticmethod
    def get_vendor_suggestions(user_id, limit=10):
        """Get vendor suggestions based on user preferences and past interactions"""
        try:
            # Get user preferences
            user = db.get_user_by_id(user_id)
            preferences = user.get('category_preferences', '') if user else ''
            
            # Get user interaction history
            conn = db.get_connection()
            c = conn.cursor()
            
            # Get vendors the user has already interacted with
            c.execute('''SELECT DISTINCT vendor_id FROM traffic 
                        WHERE user_id = ? OR (user_id IS NULL AND session_id IN 
                        (SELECT session_id FROM traffic WHERE user_id = ?))
                        ORDER BY viewed_at DESC LIMIT 20''', (user_id, user_id))
            
            viewed_vendors = [row[0] for row in c.fetchall()]
            
            # Get top vendors by traffic in user's preferred categories
            preferred_cats = preferences.split(',') if preferences else []
            suggestions = []
            
            if preferred_cats:
                placeholders = ','.join(['?' for _ in preferred_cats])
                c.execute(f'''SELECT v.*, COUNT(t.id) as view_count
                            FROM vendors v
                            LEFT JOIN traffic t ON v.id = t.vendor_id
                            WHERE v.is_active = 1 AND v.category IN ({placeholders})
                            AND v.id NOT IN ({','.join(['?' for _ in viewed_vendors])})
                            GROUP BY v.id
                            ORDER BY view_count DESC, v.rating DESC
                            LIMIT ?''',
                        preferred_cats + viewed_vendors + [limit])
                
                suggestions = [dict(row) for row in c.fetchall()]
            
            # If not enough suggestions, add nearby high-rated vendors
            if len(suggestions) < limit:
                remaining = limit - len(suggestions)
                excluded = viewed_vendors + [s['id'] for s in suggestions]
                placeholders = ','.join(['?' for _ in excluded])
                c.execute(f'''SELECT v.*, COUNT(t.id) as view_count
                            FROM vendors v
                            LEFT JOIN traffic t ON v.id = t.vendor_id
                            WHERE v.is_active = 1 
                            AND v.id NOT IN ({placeholders})
                            GROUP BY v.id
                            ORDER BY v.rating DESC, view_count DESC
                            LIMIT ?''',
                        excluded + [remaining])
                
                suggestions.extend([dict(row) for row in c.fetchall()])
            
            conn.close()
            return suggestions[:limit]
            
        except Exception as e:
            print(f"Error getting vendor suggestions: {e}")
            return []
    
    @staticmethod
    def get_product_suggestions(user_id, limit=10):
        """Get product suggestions based on user preferences and viewing history"""
        try:
            # Get user preferences
            user = db.get_user_by_id(user_id)
            preferences = user.get('category_preferences', '') if user else ''
            preferred_cats = preferences.split(',') if preferences else []
            
            conn = db.get_connection()
            c = conn.cursor()
            
            # Get products user hasn't seen
            c.execute('''SELECT DISTINCT product_id FROM traffic 
                        WHERE user_id = ? AND target_type = 'product'
                        ORDER BY viewed_at DESC''', (user_id,))
            
            viewed_products = [row[0] for row in c.fetchall()]
            
            suggestions = []
            
            # Get products in preferred categories with highest ratings
            if preferred_cats:
                placeholders = ','.join(['?' for _ in preferred_cats])
                c.execute(f'''SELECT p.*, v.business_name, COUNT(r.id) as review_count
                            FROM products p
                            JOIN vendors v ON p.vendor_id = v.id
                            LEFT JOIN reviews r ON p.id = r.product_id
                            WHERE p.is_active = 1 AND v.is_active = 1
                            AND p.category IN ({placeholders})
                            AND p.id NOT IN ({','.join(['?' for _ in viewed_products] or ['NULL'])})
                            GROUP BY p.id
                            ORDER BY p.rating DESC, review_count DESC
                            LIMIT ?''',
                        preferred_cats + (viewed_products or []) + [limit])
                
                suggestions = [dict(row) for row in c.fetchall()]
            
            # Add trending products
            if len(suggestions) < limit:
                remaining = limit - len(suggestions)
                excluded = viewed_products + [s['id'] for s in suggestions]
                
                # Get trending products from last 7 days
                seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
                placeholders = ','.join(['?' for _ in excluded] or ['NULL'])
                c.execute(f'''SELECT p.*, v.business_name, COUNT(r.id) as review_count
                            FROM products p
                            JOIN vendors v ON p.vendor_id = v.id
                            LEFT JOIN reviews r ON p.id = r.product_id
                            LEFT JOIN traffic t ON p.id = t.target_id AND t.target_type = 'product'
                            WHERE p.is_active = 1 AND v.is_active = 1
                            AND (t.viewed_at IS NULL OR t.viewed_at >= ?)
                            AND p.id NOT IN ({placeholders})
                            GROUP BY p.id
                            ORDER BY COUNT(t.id) DESC, p.rating DESC
                            LIMIT ?''',
                        [seven_days_ago] + (excluded or []) + [remaining])
                
                suggestions.extend([dict(row) for row in c.fetchall()])
            
            conn.close()
            return suggestions[:limit]
            
        except Exception as e:
            print(f"Error getting product suggestions: {e}")
            return []
    
    @staticmethod
    def get_vendor_operation_suggestions(vendor_id):
        """Get business suggestions for vendors based on their sales data and traffic"""
        try:
            conn = db.get_connection()
            c = conn.cursor()
            
            # Get vendor's products and their performance
            c.execute('''SELECT p.*, COUNT(DISTINCT r.id) as review_count,
                        AVG(r.rating) as avg_rating, COUNT(DISTINCT t.id) as view_count
                        FROM products p
                        LEFT JOIN reviews r ON p.id = r.product_id
                        LEFT JOIN traffic t ON p.id = t.target_id AND t.target_type = 'product'
                        WHERE p.vendor_id = ?
                        GROUP BY p.id
                        ORDER BY p.rating DESC''', (vendor_id,))
            
            products = [dict(row) for row in c.fetchall()]
            
            # Get traffic patterns
            c.execute('''SELECT DATE(viewed_at) as visit_date, COUNT(*) as visitor_count
                        FROM traffic
                        WHERE vendor_id = ? AND viewed_at >= datetime('now', '-30 days')
                        GROUP BY DATE(viewed_at)
                        ORDER BY visitor_count DESC''', (vendor_id,))
            
            traffic_patterns = [dict(row) for row in c.fetchall()]
            
            # Get top performing categories
            c.execute('''SELECT p.category, COUNT(*) as sales_count, AVG(p.rating) as avg_rating
                        FROM products p
                        LEFT JOIN reviews r ON p.id = r.product_id
                        WHERE p.vendor_id = ?
                        GROUP BY p.category
                        ORDER BY sales_count DESC''', (vendor_id,))
            
            top_categories = [dict(row) for row in c.fetchall()]
            
            # Generate suggestions
            suggestions = {
                'best_products': products[:5],
                'traffic_insights': traffic_patterns[:7],
                'top_categories': top_categories,
                'recommendations': []
            }
            
            # Add specific recommendations
            if products:
                low_rated = [p for p in products if p.get('avg_rating', 5) < 4]
                if low_rated:
                    suggestions['recommendations'].append({
                        'type': 'improve_quality',
                        'message': f'Improve quality of {low_rated[0]["name"]} - it has lower ratings',
                        'products': low_rated[:3]
                    })
                
                low_traffic = [p for p in products if p.get('view_count', 0) < 10]
                if low_traffic:
                    suggestions['recommendations'].append({
                        'type': 'promote_products',
                        'message': f'Promote {low_traffic[0]["name"]} - it needs more visibility',
                        'products': low_traffic[:3]
                    })
            
            if top_categories:
                best_cat = top_categories[0]
                suggestions['recommendations'].append({
                    'type': 'expand_category',
                    'message': f'Expand {best_cat["category"]} products - your best performing category',
                    'category': best_cat['category']
                })
            
            conn.close()
            return suggestions
            
        except Exception as e:
            print(f"Error getting vendor suggestions: {e}")
            return {}
