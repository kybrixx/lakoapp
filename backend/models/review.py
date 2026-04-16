from datetime import datetime
from typing import Optional, List
import json

class Review:
    def __init__(self, data: dict = None):
        self.id: Optional[str] = None
        self.customer_id: str = ""
        self.vendor_id: str = ""
        self.product_id: Optional[str] = None
        self.rating: int = 0
        self.title: Optional[str] = None
        self.comment: Optional[str] = None
        self.images: Optional[str] = None
        self.helpful_count: int = 0
        self.is_hidden: bool = False
        self.created_at: Optional[datetime] = None
        self.updated_at: Optional[datetime] = None
        
        # Joined fields
        self.customer_name: Optional[str] = None
        self.customer_avatar: Optional[str] = None
        self.vendor_name: Optional[str] = None
        
        if data:
            self.from_dict(data)
    
    def from_dict(self, data: dict):
        self.id = data.get('id')
        self.customer_id = data.get('customer_id', '')
        self.vendor_id = data.get('vendor_id', '')
        self.product_id = data.get('product_id')
        self.rating = data.get('rating', 0)
        self.title = data.get('title')
        self.comment = data.get('comment')
        self.images = data.get('images')
        self.helpful_count = data.get('helpful_count', 0)
        self.is_hidden = bool(data.get('is_hidden', 0))
        self.created_at = data.get('created_at')
        self.updated_at = data.get('updated_at')
        self.customer_name = data.get('customer_name')
        self.customer_avatar = data.get('customer_avatar')
        self.vendor_name = data.get('vendor_name')
        return self
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'vendor_id': self.vendor_id,
            'product_id': self.product_id,
            'rating': self.rating,
            'title': self.title,
            'comment': self.comment,
            'images': self.images,
            'helpful_count': self.helpful_count,
            'is_hidden': self.is_hidden,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'customer_name': self.customer_name,
            'customer_avatar': self.customer_avatar,
            'vendor_name': self.vendor_name
        }
    
    def get_image_list(self) -> List[str]:
        if not self.images:
            return []
        try:
            return json.loads(self.images)
        except:
            return [self.images] if self.images else []