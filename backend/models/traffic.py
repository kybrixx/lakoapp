from datetime import datetime
from typing import Optional

class TrafficLog:
    def __init__(self, data: dict = None):
        self.id: Optional[str] = None
        self.vendor_id: Optional[str] = None
        self.user_id: Optional[str] = None
        self.latitude: Optional[float] = None
        self.longitude: Optional[float] = None
        self.action: str = "view"
        self.created_at: Optional[datetime] = None
        
        if data:
            self.from_dict(data)
    
    def from_dict(self, data: dict):
        self.id = data.get('id')
        self.vendor_id = data.get('vendor_id')
        self.user_id = data.get('user_id')
        self.latitude = data.get('latitude')
        self.longitude = data.get('longitude')
        self.action = data.get('action', 'view')
        self.created_at = data.get('created_at')
        return self
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'vendor_id': self.vendor_id,
            'user_id': self.user_id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'action': self.action,
            'created_at': self.created_at
        }