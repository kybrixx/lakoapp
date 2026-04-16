from datetime import datetime
from typing import Optional

class Activity:
    def __init__(self, data: dict = None):
        self.id: Optional[str] = None
        self.user_id: str = ""
        self.user_role: str = ""
        self.action_type: str = ""
        self.target_type: Optional[str] = None
        self.target_id: Optional[str] = None
        self.details: Optional[str] = None
        self.created_at: Optional[datetime] = None
        
        if data:
            self.from_dict(data)
    
    def from_dict(self, data: dict):
        self.id = data.get('id')
        self.user_id = data.get('user_id', '')
        self.user_role = data.get('user_role', '')
        self.action_type = data.get('action_type', '')
        self.target_type = data.get('target_type')
        self.target_id = data.get('target_id')
        self.details = data.get('details')
        self.created_at = data.get('created_at')
        return self
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_role': self.user_role,
            'action_type': self.action_type,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'details': self.details,
            'created_at': self.created_at
        }