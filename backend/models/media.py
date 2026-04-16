from datetime import datetime
from typing import Optional

class Media:
    def __init__(self, data: dict = None):
        self.id: Optional[str] = None
        self.user_id: str = ""
        self.filename: str = ""
        self.original_path: Optional[str] = None
        self.compressed_path: Optional[str] = None
        self.thumbnail_path: Optional[str] = None
        self.file_size: Optional[int] = None
        self.mime_type: Optional[str] = None
        self.width: Optional[int] = None
        self.height: Optional[int] = None
        self.upload_type: str = "general"
        self.created_at: Optional[datetime] = None
        
        if data:
            self.from_dict(data)
    
    def from_dict(self, data: dict):
        self.id = data.get('id')
        self.user_id = data.get('user_id', '')
        self.filename = data.get('filename', '')
        self.original_path = data.get('original_path')
        self.compressed_path = data.get('compressed_path')
        self.thumbnail_path = data.get('thumbnail_path')
        self.file_size = data.get('file_size')
        self.mime_type = data.get('mime_type')
        self.width = data.get('width')
        self.height = data.get('height')
        self.upload_type = data.get('upload_type', 'general')
        self.created_at = data.get('created_at')
        return self
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'filename': self.filename,
            'original_path': self.original_path,
            'compressed_path': self.compressed_path,
            'thumbnail_path': self.thumbnail_path,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'width': self.width,
            'height': self.height,
            'upload_type': self.upload_type,
            'created_at': self.created_at
        }