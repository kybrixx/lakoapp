from datetime import datetime
from typing import Optional, List
import json

class Product:
    def __init__(self, data: dict = None):
        self.id: Optional[str] = None
        self.vendor_id: str = ""
        self.name: str = ""
        self.description: Optional[str] = None
        self.category: Optional[str] = None
        self.price: Optional[float] = None
        self.moq: Optional[int] = None
        self.stock: int = 0
        self.images: Optional[str] = None
        self.rating: float = 0.0
        self.review_count: int = 0
        self.is_active: bool = True
        self.created_at: Optional[datetime] = None
        self.updated_at: Optional[datetime] = None
        
        if data:
            self.from_dict(data)
    
    def from_dict(self, data: dict):
        self.id = data.get('id')
        self.vendor_id = data.get('vendor_id', '')
        self.name = data.get('name', '')
        self.description = data.get('description')
        self.category = data.get('category')
        self.price = data.get('price')
        self.moq = data.get('moq')
        self.stock = data.get('stock', 0)
        self.images = data.get('images')
        self.rating = data.get('rating', 0.0)
        self.review_count = data.get('review_count', 0)
        self.is_active = bool(data.get('is_active', 1))
        self.created_at = data.get('created_at')
        self.updated_at = data.get('updated_at')
        return self
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'vendor_id': self.vendor_id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'price': self.price,
            'moq': self.moq,
            'stock': self.stock,
            'images': self.images,
            'rating': self.rating,
            'review_count': self.review_count,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def get_image_list(self) -> List[str]:
        if not self.images:
            return []
        try:
            return json.loads(self.images)
        except:
            return [self.images] if self.images else []