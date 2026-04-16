from datetime import datetime
from typing import Optional

class SyncMetadata:
    def __init__(self, data: dict = None):
        self.id: Optional[str] = None
        self.user_id: str = ""
        self.table_name: str = ""
        self.last_sync: Optional[datetime] = None
        self.created_at: Optional[datetime] = None
        
        if data:
            self.from_dict(data)
    
    def from_dict(self, data: dict):
        self.id = data.get('id')
        self.user_id = data.get('user_id', '')
        self.table_name = data.get('table_name', '')
        self.last_sync = data.get('last_sync')
        self.created_at = data.get('created_at')
        return self
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'table_name': self.table_name,
            'last_sync': self.last_sync,
            'created_at': self.created_at
        }