from flask import Blueprint, request, jsonify
from auth import Auth
from database import db

chat_bp = Blueprint('chat', __name__)

@chat_bp.before_request
def check_auth():
    token = request.headers.get('X-Session-Token')
    user = Auth.get_user_by_token(token)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    if user.get('is_suspended'):
        return jsonify({'error': 'Account suspended'}), 403
    request.user = user

@chat_bp.route('/conversations', methods=['GET'])
def get_conversations():
    conversations = db.get_conversations(request.user['id'])
    return jsonify({'conversations': conversations}), 200

@chat_bp.route('/messages/<user_id>', methods=['GET'])
def get_messages(user_id):
    limit = request.args.get('limit', 50, type=int)
    messages = db.get_messages(request.user['id'], user_id, limit)
    return jsonify({'messages': messages}), 200

@chat_bp.route('/send', methods=['POST'])
def send_message():
    data = request.get_json()
    receiver_id = data.get('receiver_id')
    message = data.get('message')
    images = data.get('images')
    
    if not receiver_id:
        return jsonify({'error': 'Receiver ID required'}), 400
    
    if not message and not images:
        return jsonify({'error': 'Message or image required'}), 400
    
    message_id = db.send_message(request.user['id'], receiver_id, message, images)
    return jsonify({'id': message_id, 'sent': True}), 201

@chat_bp.route('/mark-read/<sender_id>', methods=['POST'])
def mark_as_read(sender_id):
    conn = db.get_connection()
    c = conn.cursor()
    c.execute('''UPDATE messages SET is_read = 1 
                 WHERE sender_id = ? AND receiver_id = ? AND is_read = 0''',
              (sender_id, request.user['id']))
    conn.commit()
    conn.close()
    return jsonify({'marked': True}), 200

@chat_bp.route('/unread-count', methods=['GET'])
def get_unread_count():
    conn = db.get_connection()
    c = conn.cursor()
    c.execute('SELECT SUM(unread_count) FROM conversations WHERE user1_id = ? OR user2_id = ?',
              (request.user['id'], request.user['id']))
    result = c.fetchone()
    conn.close()
    return jsonify({'unread': result[0] or 0}), 200