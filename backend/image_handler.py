import os
import uuid
from PIL import Image
from config import config

class ImageHandler:
    @staticmethod
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS
    
    @staticmethod
    def compress_image(file, upload_type='general'):
        try:
            img = Image.open(file)
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"{uuid.uuid4()}.{ext}"
            
            # Resize if needed
            if img.width > config.COMPRESSED_SIZE[0] or img.height > config.COMPRESSED_SIZE[1]:
                img.thumbnail(config.COMPRESSED_SIZE, Image.Resampling.LANCZOS)
            
            # Convert RGBA to RGB
            if img.mode == 'RGBA':
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[3])
                img = rgb_img
            
            # Save compressed
            upload_path = os.path.join(config.UPLOAD_FOLDER, 'compressed', upload_type)
            os.makedirs(upload_path, exist_ok=True)
            compressed_path = os.path.join(upload_path, filename)
            img.save(compressed_path, 'JPEG', quality=config.IMAGE_QUALITY, optimize=True)
            
            # Create thumbnail
            thumb_path = os.path.join(config.UPLOAD_FOLDER, 'thumbnails', upload_type)
            os.makedirs(thumb_path, exist_ok=True)
            thumbnail_path = os.path.join(thumb_path, filename)
            img.thumbnail(config.THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
            img.save(thumbnail_path, 'JPEG', quality=70)
            
            return {
                'success': True,
                'filename': filename,
                'compressed_path': compressed_path,
                'thumbnail_path': thumbnail_path,
                'size': os.path.getsize(compressed_path)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def save_original(file, upload_type='general'):
        try:
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"{uuid.uuid4()}.{ext}"
            upload_path = os.path.join(config.UPLOAD_FOLDER, 'originals', upload_type)
            os.makedirs(upload_path, exist_ok=True)
            filepath = os.path.join(upload_path, filename)
            file.save(filepath)
            return {'success': True, 'filename': filename, 'path': filepath}
        except Exception as e:
            return {'success': False, 'error': str(e)}