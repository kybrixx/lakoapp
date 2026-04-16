from database import db
from utils import check_profanity

class ChatService:
    @staticmethod
    def get_conversations(user_id):
        return db.get_conversations(user_id)
    
    @staticmethod
    def get_messages(user_id, other_user_id, limit=50):
        return db.get_messages(user_id, other_user_id, limit)
    
    @staticmethod
    def send_message(sender_id, receiver_id, message, images=None):
        # Check profanity
        if message:
            profanity = check_profanity(message)
            if profanity['has_profanity']:
                return {'success': False, 'error': 'Message contains inappropriate language'}
        
        message_id = db.send_message(sender_id, receiver_id, message, images)
        db.log_activity(sender_id, 'user', 'send_message', target_type='user', target_id=receiver_id)
        
        return {'success': True, 'message_id': message_id}
    
    @staticmethod
    def mark_as_read(user_id, sender_id):
        conn = db.get_connection()
        c = conn.cursor()
        c.execute('''UPDATE messages SET is_read = 1 
                     WHERE sender_id = ? AND receiver_id = ? AND is_read = 0''',
                  (sender_id, user_id))
        conn.commit()
        conn.close()
        return {'marked': True}
    
    @staticmethod
    def get_unread_count(user_id):
        conn = db.get_connection()
        c = conn.cursor()
        c.execute('''SELECT SUM(unread_count) FROM conversations 
                     WHERE user1_id = ? OR user2_id = ?''', (user_id, user_id))
        result = c.fetchone()
        conn.close()
        return result[0] or 0
    
    @staticmethod
    def can_message(sender_id, receiver_id):
        # Check if users can message each other
        sender = db.get_user_by_id(sender_id)
        receiver = db.get_user_by_id(receiver_id)
        
        if not sender or not receiver:
            return {'allowed': False, 'reason': 'User not found'}
        
        if sender.get('is_suspended') or receiver.get('is_suspended'):
            return {'allowed': False, 'reason': 'Account suspended'}
        
        return {'allowed': True}