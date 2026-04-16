from database import db
from utils import check_profanity

class FeedService:
    @staticmethod
    def get_feed(user_id=None, page=1, per_page=20):
        offset = (page - 1) * per_page
        posts = db.get_feed_posts(per_page, offset)
        
        # Check if user liked each post
        if user_id:
            for post in posts:
                post['is_liked'] = FeedService.check_user_liked(post['id'], user_id)
        
        return {
            'posts': posts,
            'page': page,
            'per_page': per_page,
            'has_more': len(posts) == per_page
        }
    
    @staticmethod
    def check_user_liked(post_id, user_id):
        conn = db.get_connection()
        c = conn.cursor()
        c.execute('SELECT id FROM post_likes WHERE post_id = ? AND user_id = ?', (post_id, user_id))
        result = c.fetchone()
        conn.close()
        return result is not None
    
    @staticmethod
    def create_post(user_id, user_role, content, images=None, parent_id=None):
        profanity = check_profanity(content)
        if profanity['has_profanity']:
            return {'success': False, 'error': 'Content contains inappropriate language'}
        
        post_id = db.create_post(user_id, user_role, content, images, parent_id)
        db.log_activity(user_id, user_role, 'create_post', target_type='post', target_id=post_id)
        
        return {'success': True, 'post_id': post_id}
    
    @staticmethod
    def get_post(post_id, user_id=None):
        post = db.get_post_by_id(post_id)
        if not post:
            return None
        
        replies = db.get_post_replies(post_id)
        post['replies'] = replies
        
        if user_id:
            post['is_liked'] = FeedService.check_user_liked(post_id, user_id)
            for reply in post['replies']:
                reply['is_liked'] = FeedService.check_user_liked(reply['id'], user_id)
        
        return post
    
    @staticmethod
    def like_post(post_id, user_id):
        liked = db.like_post(post_id, user_id)
        return {'liked': liked}
    
    @staticmethod
    def delete_post(post_id, user_id, user_role):
        post = db.get_post_by_id(post_id)
        if not post:
            return {'success': False, 'error': 'Post not found'}
        
        # Check permission
        if user_role != 'admin' and post['user_id'] != user_id:
            return {'success': False, 'error': 'Permission denied'}
        
        db.delete_post(post_id)
        db.log_activity(user_id, user_role, 'delete_post', target_type='post', target_id=post_id)
        
        return {'success': True}
    
    @staticmethod
    def get_trending_posts(limit=10):
        conn = db.get_connection()
        c = conn.cursor()
        
        # Posts with most likes in last 24 hours
        c.execute('''SELECT p.*, u.full_name as user_name, u.avatar as user_avatar
                     FROM posts p JOIN users u ON p.user_id = u.id 
                     WHERE p.parent_id IS NULL 
                     AND p.created_at >= datetime('now', '-1 day')
                     ORDER BY p.likes DESC LIMIT ?''', (limit,))
        
        posts = [dict(row) for row in c.fetchall()]
        conn.close()
        return posts
    
    @staticmethod
    def get_vendor_posts(vendor_id, limit=20):
        conn = db.get_connection()
        c = conn.cursor()
        
        c.execute('''SELECT p.* FROM posts p 
                     JOIN vendors v ON p.user_id = v.user_id 
                     WHERE v.id = ? AND p.parent_id IS NULL
                     ORDER BY p.created_at DESC LIMIT ?''', (vendor_id, limit))
        
        posts = [dict(row) for row in c.fetchall()]
        conn.close()
        return posts