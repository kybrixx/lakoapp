import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    IS_RENDER = os.getenv('RENDER', 'false').lower() == 'true'
    
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///lako.db')
    if IS_RENDER and DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://')
    
    DEFAULT_LAT = float(os.getenv('DEFAULT_LAT')) if os.getenv('DEFAULT_LAT') else None
    DEFAULT_LNG = float(os.getenv('DEFAULT_LNG')) if os.getenv('DEFAULT_LNG') else None
    DEFAULT_RADIUS_KM = float(os.getenv('DEFAULT_RADIUS_KM', 10))
    
    UPLOAD_FOLDER = 'uploads'
    MAX_IMAGE_SIZE = 5 * 1024 * 1024
    THUMBNAIL_SIZE = (200, 200)
    COMPRESSED_SIZE = (800, 800)
    IMAGE_QUALITY = 85
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

config = Config()