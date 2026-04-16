from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
import os
from config import config
from database import db
from routes import register_routes

app = Flask(__name__, static_folder='../frontend', static_url_path='')
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = config.MAX_IMAGE_SIZE

CORS(app, origins="*", supports_credentials=True)
socketio = SocketIO(app, cors_allowed_origins="*")

# Register all routes
register_routes(app)

# Serve frontend static files
@app.route('/')
def serve_index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join('../frontend', path)):
        return send_from_directory('../frontend', path)
    return send_from_directory('../frontend', 'index.html')

# Socket.IO for real-time chat
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('join')
def handle_join(data):
    room = data.get('room')
    if room:
        from flask_socketio import join_room
        join_room(room)

@socketio.on('message')
def handle_message(data):
    from flask_socketio import emit
    sender_id = data.get('sender_id')
    receiver_id = data.get('receiver_id')
    message = data.get('message')
    images = data.get('images')
    
    # Save to database
    db.send_message(sender_id, receiver_id, message, images)
    
    # Emit to receiver
    room = f"user_{receiver_id}"
    emit('message', {
        'sender_id': sender_id,
        'message': message,
        'images': images,
        'timestamp': data.get('timestamp')
    }, room=room)

if __name__ == '__main__':
    print("=" * 50)
    print("📍 LAKO Server Starting...")
    print("=" * 50)
    print(f"🌐 Local: http://localhost:{config.PORT}")
    print(f"📡 Debug: {config.DEBUG}")
    print(f"🗄️ Database: {config.DATABASE_URL}")
    print("=" * 50)
    
    if config.IS_RENDER:
        # Production on Render
        socketio.run(app, host='0.0.0.0', port=config.PORT)
    else:
        # Local development
        socketio.run(app, host='0.0.0.0', port=config.PORT, debug=config.DEBUG)