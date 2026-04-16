#!/usr/bin/env python3
"""
Lako Backend Startup Script
Run from backend directory: python run.py
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from main import app, socketio
from config import config

if __name__ == '__main__':
    print("=" * 50)
    print("📍 LAKO Backend Server")
    print("=" * 50)
    print(f"🌐 URL: http://localhost:{config.PORT}")
    print(f"📡 Debug: {config.DEBUG}")
    print(f"🗄️  Database: {config.DATABASE_URL}")
    print("=" * 50)
    print("📋 API Endpoints:")
    print(f"   POST /api/auth/register/customer")
    print(f"   POST /api/auth/login")
    print(f"   GET  /api/guest/vendors")
    print(f"   GET  /api/customer/feed")
    print(f"   GET  /api/vendor/dashboard")
    print(f"   GET  /api/admin/stats")
    print("=" * 50)
    print("🚀 Starting server...")
    print("   Press CTRL+C to stop")
    print("=" * 50)
    
    if config.IS_RENDER:
        # Production on Render
        socketio.run(app, host='0.0.0.0', port=config.PORT)
    else:
        # Local development
        socketio.run(app, host='0.0.0.0', port=config.PORT, debug=config.DEBUG)