from datetime import datetime
from database import db

class SyncService:
    @staticmethod
    def pull_changes(user_id, tables=None):
        if tables is None:
            tables = ['vendors', 'products', 'posts', 'reviews', 'messages']
        
        result = {}
        for table in tables:
            last_sync = SyncService.get_last_sync(user_id, table)
            result[table] = db.get_changes_since(user_id, table, last_sync)
        
        return result
    
    @staticmethod
    def push_changes(user_id, changes):
        results = []
        for change in changes:
            table = change.get('table')
            action = change.get('action')
            data = change.get('data')
            
            if action == 'INSERT':
                result = SyncService.handle_insert(table, data)
            elif action == 'UPDATE':
                result = SyncService.handle_update(table, data)
            elif action == 'DELETE':
                result = SyncService.handle_delete(table, data)
            else:
                result = {'success': False, 'error': 'Invalid action'}
            
            if result.get('success'):
                db.update_sync_timestamp(user_id, table)
            
            results.append(result)
        
        return results
    
    @staticmethod
    def handle_insert(table, data):
        # Implementation depends on table
        return {'success': True, 'id': data.get('id')}
    
    @staticmethod
    def handle_update(table, data):
        return {'success': True}
    
    @staticmethod
    def handle_delete(table, data):
        return {'success': True}
    
    @staticmethod
    def get_last_sync(user_id, table):
        conn = db.get_connection()
        c = conn.cursor()
        c.execute('SELECT last_sync FROM sync_metadata WHERE user_id = ? AND table_name = ?', 
                  (user_id, table))
        result = c.fetchone()
        conn.close()
        return result['last_sync'] if result else None
    
    @staticmethod
    def get_sync_status(user_id):
        tables = ['vendors', 'products', 'posts', 'reviews', 'messages', 'activities']
        status = {}
        for table in tables:
            last = SyncService.get_last_sync(user_id, table)
            status[table] = {'last_sync': last, 'synced': last is not None}
        return status