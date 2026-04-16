import math
import requests
import json
from database import db
from utils import calculate_distance
from config import config

class MapService:
    # OSM Nominatim API for geocoding
    NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
    NOMINATIM_REVERSE_URL = "https://nominatim.openstreetmap.org/reverse"
    
    # OSM Routing API (OSRM)
    OSRM_URL = "https://router.project-osrm.org/route/v1"
    
    # OSM Tile Server (for frontend)
    TILE_SERVER = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
    
    @staticmethod
    def get_nearby_vendors(lat, lng, radius_km=10, category=None):
        """Get vendors within radius using OSM data"""
        if lat is None or lng is None:
            return []
        vendors = db.get_vendors_nearby(lat, lng, radius_km, category)
        for v in vendors:
            if v.get('latitude') and v.get('longitude'):
                v['distance'] = round(calculate_distance(lat, lng, v['latitude'], v['longitude']), 2)
        vendors.sort(key=lambda x: x.get('distance', float('inf')))
        return vendors
    
    @staticmethod
    def get_heatmap_data():
        """Get traffic heatmap data"""
        return db.get_heatmap_data()
    
    @staticmethod
    def get_traffic_level(vendor_id):
        """Get vendor traffic level"""
        vendor = db.get_vendor_by_id(vendor_id)
        if not vendor:
            return {'level': 'low', 'score': 0}
        score = vendor.get('traffic_count', 0)
        if score > 1000:
            return {'level': 'high', 'score': score}
        elif score > 500:
            return {'level': 'medium', 'score': score}
        return {'level': 'low', 'score': score}
    
    @staticmethod
    def geocode_address(address):
        """
        Convert address to coordinates using OSM Nominatim
        Returns: {'lat': float, 'lng': float, 'display_name': str}
        """
        try:
            params = {
                'q': address,
                'format': 'json',
                'limit': 1,
                'addressdetails': 1
            }
            headers = {
                'User-Agent': 'Lako/1.0 (your-email@example.com)'  # Required by Nominatim
            }
            response = requests.get(MapService.NOMINATIM_URL, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    return {
                        'success': True,
                        'lat': float(data[0]['lat']),
                        'lng': float(data[0]['lon']),
                        'display_name': data[0].get('display_name', address)
                    }
            return {'success': False, 'error': 'Address not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def reverse_geocode(lat, lng):
        """
        Convert coordinates to address using OSM Nominatim
        Returns: {'display_name': str, 'address': dict}
        """
        try:
            params = {
                'lat': lat,
                'lon': lng,
                'format': 'json',
                'addressdetails': 1
            }
            headers = {
                'User-Agent': 'Lako/1.0 (your-email@example.com)'
            }
            response = requests.get(MapService.NOMINATIM_REVERSE_URL, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'display_name': data.get('display_name', ''),
                    'address': data.get('address', {})
                }
            return {'success': False, 'error': 'Location not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_route(start_lat, start_lng, end_lat, end_lng, mode='driving'):
        """
        Get route between two points using OSRM
        mode: 'driving', 'walking', 'cycling'
        Returns: {'distance_km': float, 'duration_min': float, 'geometry': dict}
        """
        try:
            # OSRM expects coordinates as: lng,lat
            coordinates = f"{start_lng},{start_lat};{end_lng},{end_lat}"
            url = f"{MapService.OSRM_URL}/{mode}/{coordinates}"
            
            params = {
                'overview': 'full',
                'geometries': 'geojson',
                'steps': 'true'
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('routes'):
                    route = data['routes'][0]
                    return {
                        'success': True,
                        'distance_km': round(route['distance'] / 1000, 2),
                        'duration_min': round(route['duration'] / 60, 1),
                        'geometry': route['geometry']
                    }
            return {'success': False, 'error': 'No route found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def is_within_geofence(lat, lng, center_lat, center_lng, radius_km):
        """Check if point is within geofence radius"""
        distance = calculate_distance(lat, lng, center_lat, center_lng)
        return distance <= radius_km
    
    @staticmethod
    def get_map_config():
        """Return map configuration for frontend"""
        return {
            'tile_server': MapService.TILE_SERVER,
            'attribution': '© OpenStreetMap contributors',
            'default_zoom': 13,
            'min_zoom': 3,
            'max_zoom': 19
        }
    
    @staticmethod
    def search_places(query, near_lat=None, near_lng=None):
        """
        Search for places using OSM Nominatim
        """
        try:
            params = {
                'q': query,
                'format': 'json',
                'limit': 10,
                'addressdetails': 1
            }
            
            # Add location bias if coordinates provided
            if near_lat and near_lng:
                params['viewbox'] = f"{near_lng-0.5},{near_lat-0.5},{near_lng+0.5},{near_lat+0.5}"
                params['bounded'] = 1
            
            headers = {
                'User-Agent': 'Lako/1.0 (your-email@example.com)'
            }
            
            response = requests.get(MapService.NOMINATIM_URL, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                places = []
                for place in response.json():
                    places.append({
                        'id': place.get('place_id'),
                        'name': place.get('display_name'),
                        'lat': float(place.get('lat', 0)),
                        'lng': float(place.get('lon', 0)),
                        'type': place.get('type'),
                        'class': place.get('class'),
                        'importance': place.get('importance')
                    })
                return {'success': True, 'places': places}
            return {'success': False, 'error': 'Search failed'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_static_map_url(lat, lng, zoom=15, width=600, height=400):
        """
        Generate static map URL using OSM static map service
        Note: OSM doesn't provide official static maps, use with caution
        """
        # Using OpenStreetMap static map alternative
        bbox = f"{lng-0.01},{lat-0.01},{lng+0.01},{lat+0.01}"
        return f"https://www.openstreetmap.org/export/embed.html?bbox={bbox}&layer=mapnik&marker={lat},{lng}"