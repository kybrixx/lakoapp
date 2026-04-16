from datetime import datetime
from typing import Optional

class User:
    def __init__(self, data: dict = None):
        self.id: Optional[str] = None
        self.email: str = ""
        self.password: str = ""
        self.role: str = "customer"
        self.full_name: Optional[str] = None
        self.phone: Optional[str] = None
        self.address: Optional[str] = None
        self.avatar: Optional[str] = None
        self.bio: Optional[str] = None
        self.category_preferences: Optional[str] = None
        self.latitude: Optional[float] = None
        self.longitude: Optional[float] = None
        self.last_location_update: Optional[datetime] = None
        self.is_suspended: bool = False
        self.suspension_until: Optional[datetime] = None
        self.suspension_reason: Optional[str] = None
        self.offense_count: int = 0
        self.eula_accepted: bool = False
        self.created_at: Optional[datetime] = None
        self.updated_at: Optional[datetime] = None
        
        if data:
            self.from_dict(data)
    
    def from_dict(self, data: dict):
        self.id = data.get('id')
        self.email = data.get('email', '')
        self.password = data.get('password', '')
        self.role = data.get('role', 'customer')
        self.full_name = data.get('full_name')
        self.phone = data.get('phone')
        self.address = data.get('address')
        self.avatar = data.get('avatar')
        self.bio = data.get('bio')
        self.category_preferences = data.get('category_preferences')
        self.latitude = data.get('latitude')
        self.longitude = data.get('longitude')
        self.last_location_update = data.get('last_location_update')
        self.is_suspended = bool(data.get('is_suspended', 0))
        self.suspension_until = data.get('suspension_until')
        self.suspension_reason = data.get('suspension_reason')
        self.offense_count = data.get('offense_count', 0)
        self.eula_accepted = bool(data.get('eula_accepted', 0))
        self.created_at = data.get('created_at')
        self.updated_at = data.get('updated_at')
        return self
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'full_name': self.full_name,
            'phone': self.phone,
            'address': self.address,
            'avatar': self.avatar,
            'bio': self.bio,
            'category_preferences': self.category_preferences,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'last_location_update': self.last_location_update,
            'is_suspended': self.is_suspended,
            'suspension_until': self.suspension_until,
            'suspension_reason': self.suspension_reason,
            'offense_count': self.offense_count,
            'eula_accepted': self.eula_accepted,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def to_safe_dict(self) -> dict:
        """Return dict without sensitive data"""
        data = self.to_dict()
        data.pop('password', None)
        return data