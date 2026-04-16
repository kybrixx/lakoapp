import sqlite3
import uuid
import bcrypt
from datetime import datetime, timedelta
from config import config

class Database:
    def __init__(self):
        self.db_path = config.DATABASE_URL.replace('sqlite:///', '') if config.DATABASE_URL.startswith('sqlite') else 'lako.db'
        self.init_db()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        conn = self.get_connection()
        c = conn.cursor()
        
        # Users table
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            full_name TEXT,
            phone TEXT,
            address TEXT,
            avatar TEXT,
            bio TEXT,
            category_preferences TEXT,
            latitude REAL,
            longitude REAL,
            last_location_update TIMESTAMP,
            is_suspended INTEGER DEFAULT 0,
            suspension_until TIMESTAMP,
            suspension_reason TEXT,
            offense_count INTEGER DEFAULT 0,
            eula_accepted INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Vendors table
        c.execute('''CREATE TABLE IF NOT EXISTS vendors (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            business_name TEXT NOT NULL,
            category TEXT NOT NULL,
            subcategory TEXT,
            description TEXT,
            address TEXT NOT NULL,
            latitude REAL,
            longitude REAL,
            phone TEXT,
            email TEXT,
            website TEXT,
            logo TEXT,
            cover_image TEXT,
            business_hours TEXT,
            rating REAL DEFAULT 0,
            review_count INTEGER DEFAULT 0,
            traffic_count INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            is_verified INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )''')
        
        # Products table
        c.execute('''CREATE TABLE IF NOT EXISTS products (
            id TEXT PRIMARY KEY,
            vendor_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT,
            price REAL,
            moq INTEGER,
            stock INTEGER DEFAULT 0,
            images TEXT,
            rating REAL DEFAULT 0,
            review_count INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (vendor_id) REFERENCES vendors(id)
        )''')
        
        # Posts table
        c.execute('''CREATE TABLE IF NOT EXISTS posts (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            user_role TEXT NOT NULL,
            content TEXT,
            images TEXT,
            likes INTEGER DEFAULT 0,
            comment_count INTEGER DEFAULT 0,
            parent_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (parent_id) REFERENCES posts(id)
        )''')
        
        # Reviews table
        c.execute('''CREATE TABLE IF NOT EXISTS reviews (
            id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            vendor_id TEXT NOT NULL,
            product_id TEXT,
            rating INTEGER NOT NULL,
            title TEXT,
            comment TEXT,
            images TEXT,
            helpful_count INTEGER DEFAULT 0,
            is_hidden INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES users(id),
            FOREIGN KEY (vendor_id) REFERENCES vendors(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )''')
        
        # Messages table
        c.execute('''CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            sender_id TEXT NOT NULL,
            receiver_id TEXT NOT NULL,
            message TEXT,
            images TEXT,
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES users(id),
            FOREIGN KEY (receiver_id) REFERENCES users(id)
        )''')
        
        # Conversations table
        c.execute('''CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            user1_id TEXT NOT NULL,
            user2_id TEXT NOT NULL,
            last_message TEXT,
            last_message_at TIMESTAMP,
            unread_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user1_id, user2_id),
            FOREIGN KEY (user1_id) REFERENCES users(id),
            FOREIGN KEY (user2_id) REFERENCES users(id)
        )''')
        
        # Traffic logs
        c.execute('''CREATE TABLE IF NOT EXISTS traffic_logs (
            id TEXT PRIMARY KEY,
            vendor_id TEXT,
            user_id TEXT,
            latitude REAL,
            longitude REAL,
            action TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (vendor_id) REFERENCES vendors(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )''')
        
        # Activities
        c.execute('''CREATE TABLE IF NOT EXISTS activities (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            user_role TEXT NOT NULL,
            action_type TEXT NOT NULL,
            target_type TEXT,
            target_id TEXT,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )''')
        
        # Shortlists
        c.execute('''CREATE TABLE IF NOT EXISTS shortlists (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            vendor_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, vendor_id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (vendor_id) REFERENCES vendors(id)
        )''')
        
        # Post likes
        c.execute('''CREATE TABLE IF NOT EXISTS post_likes (
            id TEXT PRIMARY KEY,
            post_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(post_id, user_id),
            FOREIGN KEY (post_id) REFERENCES posts(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )''')
        
        # Review likes
        c.execute('''CREATE TABLE IF NOT EXISTS review_likes (
            id TEXT PRIMARY KEY,
            review_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(review_id, user_id),
            FOREIGN KEY (review_id) REFERENCES reviews(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )''')
        
        # Sync metadata
        c.execute('''CREATE TABLE IF NOT EXISTS sync_metadata (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            table_name TEXT NOT NULL,
            last_sync TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, table_name),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )''')
        
        # Media
        c.execute('''CREATE TABLE IF NOT EXISTS media (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            filename TEXT NOT NULL,
            original_path TEXT,
            compressed_path TEXT,
            thumbnail_path TEXT,
            file_size INTEGER,
            mime_type TEXT,
            width INTEGER,
            height INTEGER,
            upload_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )''')
        
        # Create admin user
        admin_id = str(uuid.uuid4())
        admin_password = bcrypt.hashpw('admin123'.encode(), bcrypt.gensalt()).decode()
        
        try:
            c.execute('''INSERT INTO users (id, email, password, role, full_name, eula_accepted) 
                         VALUES (?, ?, ?, ?, ?, ?)''',
                      (admin_id, 'admin@lako.com', admin_password, 'admin', 'System Administrator', 1))
        except sqlite3.IntegrityError:
            pass
        
        conn.commit()
        conn.close()
        print("✓ Database initialized")
    
    # ========== USER METHODS ==========
    def create_user(self, email, password, role, full_name=None, phone=None, address=None):
        conn = self.get_connection()
        c = conn.cursor()
        user_id = str(uuid.uuid4())
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        c.execute('''INSERT INTO users (id, email, password, role, full_name, phone, address, eula_accepted)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                  (user_id, email, hashed, role, full_name, phone, address, 1))
        conn.commit()
        conn.close()
        return user_id
    
    def get_user_by_email(self, email):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        conn.close()
        return dict(user) if user else None
    
    def get_user_by_id(self, user_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = c.fetchone()
        conn.close()
        return dict(user) if user else None
    
    def verify_password(self, email, password):
        user = self.get_user_by_email(email)
        if user and bcrypt.checkpw(password.encode(), user['password'].encode()):
            return user
        return None
    
    def update_user_location(self, user_id, lat, lng):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('''UPDATE users SET latitude = ?, longitude = ?, last_location_update = ? 
                     WHERE id = ?''', (lat, lng, datetime.now(), user_id))
        conn.commit()
        conn.close()
    
    # ========== VENDOR METHODS ==========
    def create_vendor(self, user_id, business_name, category, address, lat=None, lng=None,
                      phone=None, email=None, description=None, subcategory=None):
        conn = self.get_connection()
        c = conn.cursor()
        vendor_id = str(uuid.uuid4())
        c.execute('''INSERT INTO vendors (id, user_id, business_name, category, subcategory, 
                     description, address, latitude, longitude, phone, email) 
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (vendor_id, user_id, business_name, category, subcategory, description, 
                   address, lat, lng, phone, email))
        conn.commit()
        conn.close()
        return vendor_id
    
    def get_vendors_nearby(self, lat, lng, radius_km=10, category=None):
        if lat is None or lng is None:
            return []
        
        conn = self.get_connection()
        c = conn.cursor()
        query = '''SELECT v.*, u.full_name as owner_name FROM vendors v 
                   JOIN users u ON v.user_id = u.id 
                   WHERE v.is_active = 1 AND v.latitude IS NOT NULL AND v.longitude IS NOT NULL'''
        params = []
        if category:
            query += ' AND v.category = ?'
            params.append(category)
        c.execute(query, params)
        vendors = c.fetchall()
        conn.close()
        
        result = []
        radius_deg = radius_km / 111.0
        for v in vendors:
            v_dict = dict(v)
            if v_dict['latitude'] and v_dict['longitude']:
                dist_sq = (lat - v_dict['latitude'])**2 + (lng - v_dict['longitude'])**2
                if dist_sq <= radius_deg**2:
                    result.append(v_dict)
        return result
    
    def get_vendor_by_id(self, vendor_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM vendors WHERE id = ?', (vendor_id,))
        vendor = c.fetchone()
        conn.close()
        return dict(vendor) if vendor else None
    
    def get_vendor_by_user_id(self, user_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM vendors WHERE user_id = ?', (user_id,))
        vendor = c.fetchone()
        conn.close()
        return dict(vendor) if vendor else None
    
    def update_vendor_location(self, vendor_id, lat, lng):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('UPDATE vendors SET latitude = ?, longitude = ?, updated_at = ? WHERE id = ?',
                  (lat, lng, datetime.now(), vendor_id))
        conn.commit()
        conn.close()
    
    def increment_traffic(self, vendor_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('UPDATE vendors SET traffic_count = traffic_count + 1 WHERE id = ?', (vendor_id,))
        conn.commit()
        conn.close()
    
    # ========== PRODUCT METHODS ==========
    def create_product(self, vendor_id, name, description=None, category=None, 
                       price=None, moq=None, stock=0, images=None):
        conn = self.get_connection()
        c = conn.cursor()
        product_id = str(uuid.uuid4())
        c.execute('''INSERT INTO products (id, vendor_id, name, description, category, price, moq, stock, images)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (product_id, vendor_id, name, description, category, price, moq, stock, images))
        conn.commit()
        conn.close()
        return product_id
    
    def get_products_by_vendor(self, vendor_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM products WHERE vendor_id = ? AND is_active = 1 ORDER BY created_at DESC', (vendor_id,))
        products = c.fetchall()
        conn.close()
        return [dict(p) for p in products]
    
    def get_product_by_id(self, product_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('SELECT p.*, v.business_name as vendor_name FROM products p JOIN vendors v ON p.vendor_id = v.id WHERE p.id = ?', (product_id,))
        product = c.fetchone()
        conn.close()
        return dict(product) if product else None
    
    def update_product(self, product_id, **kwargs):
        conn = self.get_connection()
        c = conn.cursor()
        fields = ', '.join([f'{k} = ?' for k in kwargs.keys()])
        values = list(kwargs.values()) + [product_id]
        c.execute(f'UPDATE products SET {fields}, updated_at = ? WHERE id = ?', 
                  values[:-1] + [datetime.now(), product_id])
        conn.commit()
        conn.close()
    
    def delete_product(self, product_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('UPDATE products SET is_active = 0, updated_at = ? WHERE id = ?', 
                  (datetime.now(), product_id))
        conn.commit()
        conn.close()
    
    # ========== POST METHODS ==========
    def create_post(self, user_id, user_role, content, images=None, parent_id=None):
        conn = self.get_connection()
        c = conn.cursor()
        post_id = str(uuid.uuid4())
        c.execute('''INSERT INTO posts (id, user_id, user_role, content, images, parent_id)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (post_id, user_id, user_role, content, images, parent_id))
        conn.commit()
        conn.close()
        return post_id
    
    def get_feed_posts(self, limit=50, offset=0):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('''SELECT p.*, u.full_name as user_name, u.avatar as user_avatar
                     FROM posts p JOIN users u ON p.user_id = u.id 
                     WHERE p.parent_id IS NULL 
                     ORDER BY p.created_at DESC LIMIT ? OFFSET ?''', (limit, offset))
        posts = c.fetchall()
        conn.close()
        return [dict(p) for p in posts]
    
    def get_post_by_id(self, post_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('''SELECT p.*, u.full_name as user_name, u.avatar as user_avatar
                     FROM posts p JOIN users u ON p.user_id = u.id WHERE p.id = ?''', (post_id,))
        post = c.fetchone()
        conn.close()
        return dict(post) if post else None
    
    def get_post_replies(self, post_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('''SELECT p.*, u.full_name as user_name, u.avatar as user_avatar
                     FROM posts p JOIN users u ON p.user_id = u.id 
                     WHERE p.parent_id = ? ORDER BY p.created_at ASC''', (post_id,))
        replies = c.fetchall()
        conn.close()
        return [dict(r) for r in replies]
    
    def like_post(self, post_id, user_id):
        conn = self.get_connection()
        c = conn.cursor()
        try:
            like_id = str(uuid.uuid4())
            c.execute('INSERT INTO post_likes (id, post_id, user_id) VALUES (?, ?, ?)',
                      (like_id, post_id, user_id))
            c.execute('UPDATE posts SET likes = likes + 1 WHERE id = ?', (post_id,))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            c.execute('DELETE FROM post_likes WHERE post_id = ? AND user_id = ?', (post_id, user_id))
            c.execute('UPDATE posts SET likes = likes - 1 WHERE id = ?', (post_id,))
            conn.commit()
            return False
        finally:
            conn.close()
    
    def delete_post(self, post_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('DELETE FROM post_likes WHERE post_id = ?', (post_id,))
        c.execute('DELETE FROM posts WHERE id = ? OR parent_id = ?', (post_id, post_id))
        conn.commit()
        conn.close()
    
    # ========== REVIEW METHODS ==========
    def create_review(self, customer_id, vendor_id, rating, title=None, comment=None, 
                      product_id=None, images=None):
        conn = self.get_connection()
        c = conn.cursor()
        review_id = str(uuid.uuid4())
        c.execute('''INSERT INTO reviews (id, customer_id, vendor_id, product_id, rating, title, comment, images)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                  (review_id, customer_id, vendor_id, product_id, rating, title, comment, images))
        c.execute('''SELECT AVG(rating) as avg_rating, COUNT(*) as count 
                     FROM reviews WHERE vendor_id = ?''', (vendor_id,))
        result = c.fetchone()
        c.execute('UPDATE vendors SET rating = ?, review_count = ? WHERE id = ?',
                  (round(result['avg_rating'], 1) if result['avg_rating'] else 0, 
                   result['count'], vendor_id))
        conn.commit()
        conn.close()
        return review_id
    
    def get_reviews_by_vendor(self, vendor_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('''SELECT r.*, u.full_name as customer_name, u.avatar as customer_avatar
                     FROM reviews r JOIN users u ON r.customer_id = u.id 
                     WHERE r.vendor_id = ? AND r.is_hidden = 0 
                     ORDER BY r.created_at DESC''', (vendor_id,))
        reviews = c.fetchall()
        conn.close()
        return [dict(r) for r in reviews]
    
    def get_reviews_by_product(self, product_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('''SELECT r.*, u.full_name as customer_name, u.avatar as customer_avatar
                     FROM reviews r JOIN users u ON r.customer_id = u.id 
                     WHERE r.product_id = ? AND r.is_hidden = 0 
                     ORDER BY r.created_at DESC''', (product_id,))
        reviews = c.fetchall()
        conn.close()
        return [dict(r) for r in reviews]
    
    # ========== CHAT METHODS ==========
    def send_message(self, sender_id, receiver_id, message, images=None):
        conn = self.get_connection()
        c = conn.cursor()
        message_id = str(uuid.uuid4())
        c.execute('''INSERT INTO messages (id, sender_id, receiver_id, message, images)
                     VALUES (?, ?, ?, ?, ?)''',
                  (message_id, sender_id, receiver_id, message, images))
        user1 = min(sender_id, receiver_id)
        user2 = max(sender_id, receiver_id)
        c.execute('SELECT id FROM conversations WHERE user1_id = ? AND user2_id = ?', (user1, user2))
        conv = c.fetchone()
        if conv:
            c.execute('''UPDATE conversations SET last_message = ?, last_message_at = ?, 
                         unread_count = unread_count + 1, updated_at = ? WHERE id = ?''',
                      (message[:100] if message else '', datetime.now(), datetime.now(), conv['id']))
        else:
            conv_id = str(uuid.uuid4())
            c.execute('''INSERT INTO conversations (id, user1_id, user2_id, last_message, last_message_at, unread_count)
                         VALUES (?, ?, ?, ?, ?, 1)''',
                      (conv_id, user1, user2, message[:100] if message else '', datetime.now()))
        conn.commit()
        conn.close()
        return message_id
    
    def get_messages(self, user1_id, user2_id, limit=50):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('''SELECT * FROM messages 
                     WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?)
                     ORDER BY created_at DESC LIMIT ?''',
                  (user1_id, user2_id, user2_id, user1_id, limit))
        messages = c.fetchall()
        c.execute('''UPDATE messages SET is_read = 1 
                     WHERE sender_id = ? AND receiver_id = ? AND is_read = 0''',
                  (user2_id, user1_id))
        conn.commit()
        conn.close()
        return [dict(m) for m in reversed(messages)]
    
    def get_conversations(self, user_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('''SELECT c.*, 
                     CASE WHEN c.user1_id = ? THEN u2.full_name ELSE u1.full_name END as other_name,
                     CASE WHEN c.user1_id = ? THEN u2.avatar ELSE u1.avatar END as other_avatar,
                     CASE WHEN c.user1_id = ? THEN u2.id ELSE u1.id END as other_id
                     FROM conversations c
                     JOIN users u1 ON c.user1_id = u1.id
                     JOIN users u2 ON c.user2_id = u2.id
                     WHERE c.user1_id = ? OR c.user2_id = ?
                     ORDER BY c.updated_at DESC''',
                  (user_id, user_id, user_id, user_id, user_id))
        conversations = c.fetchall()
        conn.close()
        return [dict(c) for c in conversations]
    
    # ========== TRAFFIC & HEATMAP METHODS ==========
    def log_traffic(self, vendor_id, user_id, lat, lng, action='view'):
        conn = self.get_connection()
        c = conn.cursor()
        log_id = str(uuid.uuid4())
        c.execute('''INSERT INTO traffic_logs (id, vendor_id, user_id, latitude, longitude, action)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (log_id, vendor_id, user_id, lat, lng, action))
        conn.commit()
        conn.close()
    
    def get_heatmap_data(self):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('''SELECT latitude, longitude, COUNT(*) as weight 
                     FROM traffic_logs 
                     WHERE latitude IS NOT NULL AND longitude IS NOT NULL
                     GROUP BY ROUND(latitude, 3), ROUND(longitude, 3)
                     ORDER BY weight DESC''')
        points = c.fetchall()
        conn.close()
        return [dict(p) for p in points]
    
    # ========== ACTIVITY METHODS ==========
    def log_activity(self, user_id, user_role, action_type, target_type=None, 
                     target_id=None, details=None):
        conn = self.get_connection()
        c = conn.cursor()
        activity_id = str(uuid.uuid4())
        c.execute('''INSERT INTO activities (id, user_id, user_role, action_type, target_type, target_id, details)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (activity_id, user_id, user_role, action_type, target_type, target_id, details))
        conn.commit()
        conn.close()
    
    def get_user_activities(self, user_id, limit=50):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('''SELECT * FROM activities WHERE user_id = ? 
                     ORDER BY created_at DESC LIMIT ?''', (user_id, limit))
        activities = c.fetchall()
        conn.close()
        return [dict(a) for a in activities]
    
    # ========== SHORTLIST METHODS ==========
    def add_to_shortlist(self, user_id, vendor_id):
        conn = self.get_connection()
        c = conn.cursor()
        try:
            shortlist_id = str(uuid.uuid4())
            c.execute('INSERT INTO shortlists (id, user_id, vendor_id) VALUES (?, ?, ?)',
                      (shortlist_id, user_id, vendor_id))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def remove_from_shortlist(self, user_id, vendor_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('DELETE FROM shortlists WHERE user_id = ? AND vendor_id = ?', (user_id, vendor_id))
        conn.commit()
        conn.close()
    
    def get_shortlist(self, user_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('''SELECT v.* FROM shortlists s 
                     JOIN vendors v ON s.vendor_id = v.id 
                     WHERE s.user_id = ? AND v.is_active = 1
                     ORDER BY s.created_at DESC''', (user_id,))
        vendors = c.fetchall()
        conn.close()
        return [dict(v) for v in vendors]
    
    def is_shortlisted(self, user_id, vendor_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('SELECT id FROM shortlists WHERE user_id = ? AND vendor_id = ?', (user_id, vendor_id))
        result = c.fetchone()
        conn.close()
        return result is not None
    
    # ========== SEARCH METHODS ==========
    def search_vendors(self, query):
        conn = self.get_connection()
        c = conn.cursor()
        search_term = f'%{query}%'
        c.execute('''SELECT * FROM vendors 
                     WHERE (business_name LIKE ? OR category LIKE ? OR description LIKE ? OR address LIKE ?)
                     AND is_active = 1 ORDER BY rating DESC''',
                  (search_term, search_term, search_term, search_term))
        vendors = c.fetchall()
        conn.close()
        return [dict(v) for v in vendors]
    
    def search_products(self, query):
        conn = self.get_connection()
        c = conn.cursor()
        search_term = f'%{query}%'
        c.execute('''SELECT p.*, v.business_name as vendor_name, v.latitude, v.longitude
                     FROM products p JOIN vendors v ON p.vendor_id = v.id
                     WHERE (p.name LIKE ? OR p.description LIKE ? OR p.category LIKE ?)
                     AND p.is_active = 1 AND v.is_active = 1
                     ORDER BY p.rating DESC''',
                  (search_term, search_term, search_term))
        products = c.fetchall()
        conn.close()
        return [dict(p) for p in products]
    
    # ========== ADMIN METHODS ==========
    def get_all_users(self, role=None):
        conn = self.get_connection()
        c = conn.cursor()
        if role:
            c.execute('SELECT * FROM users WHERE role = ? ORDER BY created_at DESC', (role,))
        else:
            c.execute('SELECT * FROM users ORDER BY created_at DESC')
        users = c.fetchall()
        conn.close()
        return [dict(u) for u in users]
    # Add this method to the Database class in database.py

    def create_media(self, user_id, filename, compressed_path, thumbnail_path, file_size, upload_type):
        conn = self.get_connection()
        c = conn.cursor()
        media_id = str(uuid.uuid4())
        c.execute('''INSERT INTO media (id, user_id, filename, compressed_path, thumbnail_path, file_size, upload_type)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (media_id, user_id, filename, compressed_path, thumbnail_path, file_size, upload_type))
        conn.commit()
        conn.close()
        return media_id
    
    def get_all_vendors(self):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('''SELECT v.*, u.email as owner_email, u.full_name as owner_name 
                     FROM vendors v JOIN users u ON v.user_id = u.id 
                     ORDER BY v.created_at DESC''')
        vendors = c.fetchall()
        conn.close()
        return [dict(v) for v in vendors]
    
    def get_stats(self):
        conn = self.get_connection()
        c = conn.cursor()
        stats = {}
        c.execute('SELECT COUNT(*) FROM users WHERE role = "customer"')
        stats['total_customers'] = c.fetchone()[0]
        c.execute('SELECT COUNT(*) FROM users WHERE role = "vendor"')
        stats['total_vendors'] = c.fetchone()[0]
        c.execute('SELECT COUNT(*) FROM products WHERE is_active = 1')
        stats['total_products'] = c.fetchone()[0]
        c.execute('SELECT COUNT(*) FROM reviews')
        stats['total_reviews'] = c.fetchone()[0]
        c.execute('SELECT COUNT(*) FROM posts')
        stats['total_posts'] = c.fetchone()[0]
        c.execute('SELECT SUM(traffic_count) FROM vendors')
        stats['total_traffic'] = c.fetchone()[0] or 0
        c.execute('SELECT COUNT(*) FROM users WHERE is_suspended = 1')
        stats['suspended_users'] = c.fetchone()[0]
        conn.close()
        return stats
    
    def suspend_user(self, user_id, reason, days=None):
        conn = self.get_connection()
        c = conn.cursor()
        if days:
            suspension_until = datetime.now() + timedelta(days=days)
            c.execute('''UPDATE users SET is_suspended = 1, suspension_until = ?, suspension_reason = ? 
                         WHERE id = ?''', (suspension_until, reason, user_id))
        else:
            c.execute('''UPDATE users SET is_suspended = 1, suspension_reason = ? WHERE id = ?''', 
                      (reason, user_id))
        conn.commit()
        conn.close()
    
    def unsuspend_user(self, user_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('''UPDATE users SET is_suspended = 0, suspension_until = NULL, suspension_reason = NULL 
                     WHERE id = ?''', (user_id,))
        conn.commit()
        conn.close()
    
    def toggle_vendor_active(self, vendor_id, is_active):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('UPDATE vendors SET is_active = ?, updated_at = ? WHERE id = ?', 
                  (is_active, datetime.now(), vendor_id))
        conn.commit()
        conn.close()
    
    def delete_user(self, user_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
    
    # ========== SYNC METHODS ==========
    def update_sync_timestamp(self, user_id, table_name):
        conn = self.get_connection()
        c = conn.cursor()
        try:
            sync_id = str(uuid.uuid4())
            c.execute('''INSERT INTO sync_metadata (id, user_id, table_name, last_sync)
                         VALUES (?, ?, ?, ?)''', (sync_id, user_id, table_name, datetime.now()))
        except sqlite3.IntegrityError:
            c.execute('''UPDATE sync_metadata SET last_sync = ? 
                         WHERE user_id = ? AND table_name = ?''',
                      (datetime.now(), user_id, table_name))
        conn.commit()
        conn.close()

# Global database instance
db = Database()