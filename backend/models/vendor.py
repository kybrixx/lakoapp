from datetime import datetime
from typing import Optional

class Vendor:
    def __init__(self, data: dict = None):
        self.id: Optional[str] = None
        self.user_id: str = ""
        self.business_name: str = ""
        self.category: str = ""
        self.subcategory: Optional[str] = None
        self.description: Optional[str] = None
        self.address: str = ""
        self.latitude: Optional[float] = None
        self.longitude: Optional[float] = None
        self.phone: Optional[str] = None
        self.email: Optional[str] = None
        self.website: Optional[str] = None
        self.logo: Optional[str] = None
        self.cover_image: Optional[str] = None
        self.business_hours: Optional[str] = None
        self.rating: float = 0.0
        self.review_count: int = 0
        self.traffic_count: int = 0
        self.is_active: bool = True
        self.is_verified: bool = False
        self.created_at: Optional[datetime] = None
        self.updated_at: Optional[datetime] = None
        
        if data:
            self.from_dict(data)
    
    def from_dict(self, data: dict):
        self.id = data.get('id')
        self.user_id = data.get('user_id', '')
        self.business_name = data.get('business_name', '')
        self.category = data.get('category', '')
        self.subcategory = data.get('subcategory')
        self.description = data.get('description')
        self.address = data.get('address', '')
        self.latitude = data.get('latitude')
        self.longitude = data.get('longitude')
        self.phone = data.get('phone')
        self.email = data.get('email')
        self.website = data.get('website')
        self.logo = data.get('logo')
        self.cover_image = data.get('cover_image')
        self.business_hours = data.get('business_hours')
        self.rating = data.get('rating', 0.0)
        self.review_count = data.get('review_count', 0)
        self.traffic_count = data.get('traffic_count', 0)
        self.is_active = bool(data.get('is_active', 1))
        self.is_verified = bool(data.get('is_verified', 0))
        self.created_at = data.get('created_at')
        self.updated_at = data.get('updated_at')
        return self
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'business_name': self.business_name,
            'category': self.category,
            'subcategory': self.subcategory,
            'description': self.description,
            'address': self.address,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'phone': self.phone,
            'email': self.email,
            'website': self.website,
            'logo': self.logo,
            'cover_image': self.cover_image,
            'business_hours': self.business_hours,
            'rating': self.rating,
            'review_count': self.review_count,
            'traffic_count': self.traffic_count,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }