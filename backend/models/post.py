from datetime import datetime
from typing import Optional, List
import json

class Post:
    def __init__(self, data: dict = None):
        self.id: Optional[str] = None
        self.user_id: str = ""
        self.user_role: str = ""
        self.content: Optional[str] = None
        self.images: Optional[str] = None
        self.likes: int = 0
        self.comment_count: int = 0
        self.parent_id: Optional[str] = None
        self.created_at: Optional[datetime] = None
        self.updated_at: Optional[datetime] = None
        
        # Joined fields
        self.user_name: Optional[str] = None
        self.user_avatar: Optional[str] = None
        self.replies: List['Post'] = []
        self.is_liked: bool = False
        
        if data:
            self.from_dict(data)
    
    def from_dict(self, data: dict):
        self.id = data.get('id')
        self.user_id = data.get('user_id', '')
        self.user_role = data.get('user_role', '')
        self.content = data.get('content')
        self.images = data.get('images')
        self.likes = data.get('likes', 0)
        self.comment_count = data.get('comment_count', 0)
        self.parent_id = data.get('parent_id')
        self.created_at = data.get('created_at')
        self.updated_at = data.get('updated_at')
        self.user_name = data.get('user_name')
        self.user_avatar = data.get('user_avatar')
        return self
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_role': self.user_role,
            'content': self.content,
            'images': self.images,
            'likes': self.likes,
            'comment_count': self.comment_count,
            'parent_id': self.parent_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'user_name': self.user_name,
            'user_avatar': self.user_avatar,
            'replies': [r.to_dict() for r in self.replies],
            'is_liked': self.is_liked
        }
    
    def get_image_list(self) -> List[str]:
        if not self.images:
            return []
        try:
            return json.loads(self.images)
        except:
            return [self.images] if self.images else []