from datetime import datetime
from typing import Optional, List
import json

class Message:
    def __init__(self, data: dict = None):
        self.id: Optional[str] = None
        self.sender_id: str = ""
        self.receiver_id: str = ""
        self.message: Optional[str] = None
        self.images: Optional[str] = None
        self.is_read: bool = False
        self.created_at: Optional[datetime] = None
        
        # Joined fields
        self.sender_name: Optional[str] = None
        self.sender_avatar: Optional[str] = None
        
        if data:
            self.from_dict(data)
    
    def from_dict(self, data: dict):
        self.id = data.get('id')
        self.sender_id = data.get('sender_id', '')
        self.receiver_id = data.get('receiver_id', '')
        self.message = data.get('message')
        self.images = data.get('images')
        self.is_read = bool(data.get('is_read', 0))
        self.created_at = data.get('created_at')
        self.sender_name = data.get('sender_name')
        self.sender_avatar = data.get('sender_avatar')
        return self
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'message': self.message,
            'images': self.images,
            'is_read': self.is_read,
            'created_at': self.created_at,
            'sender_name': self.sender_name,
            'sender_avatar': self.sender_avatar
        }
    
    def get_image_list(self) -> List[str]:
        if not self.images:
            return []
        try:
            return json.loads(self.images)
        except:
            return [self.images] if self.images else []

class Conversation:
    def __init__(self, data: dict = None):
        self.id: Optional[str] = None
        self.user1_id: str = ""
        self.user2_id: str = ""
        self.last_message: Optional[str] = None
        self.last_message_at: Optional[datetime] = None
        self.unread_count: int = 0
        self.created_at: Optional[datetime] = None
        self.updated_at: Optional[datetime] = None
        
        # Joined fields
        self.other_id: Optional[str] = None
        self.other_name: Optional[str] = None
        self.other_avatar: Optional[str] = None
        self.messages: List[Message] = []
        
        if data:
            self.from_dict(data)
    
    def from_dict(self, data: dict):
        self.id = data.get('id')
        self.user1_id = data.get('user1_id', '')
        self.user2_id = data.get('user2_id', '')
        self.last_message = data.get('last_message')
        self.last_message_at = data.get('last_message_at')
        self.unread_count = data.get('unread_count', 0)
        self.created_at = data.get('created_at')
        self.updated_at = data.get('updated_at')
        self.other_id = data.get('other_id')
        self.other_name = data.get('other_name')
        self.other_avatar = data.get('other_avatar')
        return self
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'user1_id': self.user1_id,
            'user2_id': self.user2_id,
            'last_message': self.last_message,
            'last_message_at': self.last_message_at,
            'unread_count': self.unread_count,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'other_id': self.other_id,
            'other_name': self.other_name,
            'other_avatar': self.other_avatar,
            'messages': [m.to_dict() for m in self.messages]
        }