from datetime import datetime, timedelta
from database import db
from .map_service import MapService

class TrafficService:
    @staticmethod
    def log_view(vendor_id, user_id=None, lat=None, lng=None):
        db.increment_traffic(vendor_id)
        db.log_traffic(vendor_id, user_id, lat, lng, 'view')
        return {'logged': True}
    
    @staticmethod
    def get_vendor_traffic(vendor_id):
        vendor = db.get_vendor_by_id(vendor_id)
        if not vendor:
            return {'error': 'Vendor not found'}
        
        return {
            'total_views': vendor.get('traffic_count', 0),
            'level': TrafficService.calculate_traffic_level(vendor.get('traffic_count', 0))
        }
    
    @staticmethod
    def calculate_traffic_level(count):
        if count > 1000:
            return 'high'
        elif count > 500:
            return 'medium'
        return 'low'
    
    @staticmethod
    def get_heatmap_data(lat=None, lng=None, radius_km=10):
        points = db.get_heatmap_data()
        
        if lat and lng:
            filtered = []
            for p in points:
                if p.get('latitude') and p.get('longitude'):
                    dist = MapService.calculate_distance(lat, lng, p['latitude'], p['longitude'])
                    if dist <= radius_km:
                        filtered.append(p)
            return filtered
        
        return points
    
    @staticmethod
    def get_trending_vendors(lat, lng, radius_km=10, limit=10):
        vendors = MapService.get_nearby_vendors(lat, lng, radius_km)
        
        # Sort by traffic count
        vendors.sort(key=lambda x: x.get('traffic_count', 0), reverse=True)
        return vendors[:limit]
    
    @staticmethod
    def get_traffic_insights(vendor_id):
        conn = db.get_connection()
        c = conn.cursor()
        
        # Get traffic by hour (last 7 days)
        seven_days_ago = datetime.now() - timedelta(days=7)
        c.execute('''SELECT strftime('%H', created_at) as hour, COUNT(*) as count 
                     FROM traffic_logs WHERE vendor_id = ? AND created_at >= ?
                     GROUP BY hour ORDER BY hour''', (vendor_id, seven_days_ago))
        hourly = [{'hour': row[0], 'count': row[1]} for row in c.fetchall()]
        
        # Get traffic by day
        c.execute('''SELECT strftime('%w', created_at) as day, COUNT(*) as count 
                     FROM traffic_logs WHERE vendor_id = ? AND created_at >= ?
                     GROUP BY day ORDER BY day''', (vendor_id, seven_days_ago))
        daily = [{'day': row[0], 'count': row[1]} for row in c.fetchall()]
        
        conn.close()
        
        # Find peak hours
        peak_hours = sorted(hourly, key=lambda x: x['count'], reverse=True)[:3] if hourly else []
        
        return {
            'hourly': hourly,
            'daily': daily,
            'peak_hours': peak_hours,
            'total_week': sum(h['count'] for h in hourly)
        }
    
    @staticmethod
    def get_area_traffic(lat, lng, radius_km=5):
        vendors = MapService.get_nearby_vendors(lat, lng, radius_km)
        
        total_traffic = sum(v.get('traffic_count', 0) for v in vendors)
        avg_traffic = total_traffic / len(vendors) if vendors else 0
        
        return {
            'vendors_count': len(vendors),
            'total_traffic': total_traffic,
            'average_traffic': round(avg_traffic, 1),
            'traffic_level': TrafficService.calculate_traffic_level(total_traffic)
        }