// Local Database Manager for Offline Support
class LocalDB {
    constructor() {
        this.dbName = 'lako_local';
        this.version = 1;
        this.db = null;
        this.init();
    }

    async init() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, this.version);
            
            request.onerror = () => reject(request.error);
            request.onsuccess = () => {
                this.db = request.result;
                resolve();
            };
            
            request.onupgradeneeded = (e) => {
                const db = e.target.result;
                
                // Vendors store
                if (!db.objectStoreNames.contains('vendors')) {
                    const vendorStore = db.createObjectStore('vendors', { keyPath: 'id' });
                    vendorStore.createIndex('category', 'category');
                }
                
                // Products store
                if (!db.objectStoreNames.contains('products')) {
                    const productStore = db.createObjectStore('products', { keyPath: 'id' });
                    productStore.createIndex('vendor_id', 'vendor_id');
                }
                
                // Posts store
                if (!db.objectStoreNames.contains('posts')) {
                    const postStore = db.createObjectStore('posts', { keyPath: 'id' });
                    postStore.createIndex('user_id', 'user_id');
                }
                
                // Reviews store
                if (!db.objectStoreNames.contains('reviews')) {
                    db.createObjectStore('reviews', { keyPath: 'id' });
                }
                
                // Cache store
                if (!db.objectStoreNames.contains('cache')) {
                    db.createObjectStore('cache', { keyPath: 'key' });
                }
                
                // Sync queue
                if (!db.objectStoreNames.contains('syncQueue')) {
                    const queueStore = db.createObjectStore('syncQueue', { keyPath: 'id', autoIncrement: true });
                    queueStore.createIndex('synced', 'synced');
                }
            };
        });
    }

    async save(storeName, data) {
        return new Promise((resolve, reject) => {
            const tx = this.db.transaction(storeName, 'readwrite');
            const store = tx.objectStore(storeName);
            
            if (Array.isArray(data)) {
                data.forEach(item => store.put(item));
            } else {
                store.put(data);
            }
            
            tx.oncomplete = () => resolve();
            tx.onerror = () => reject(tx.error);
        });
    }

    async get(storeName, id) {
        return new Promise((resolve, reject) => {
            const tx = this.db.transaction(storeName, 'readonly');
            const store = tx.objectStore(storeName);
            const request = id ? store.get(id) : store.getAll();
            
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    async getAll(storeName) {
        return this.get(storeName, null);
    }

    async delete(storeName, id) {
        return new Promise((resolve, reject) => {
            const tx = this.db.transaction(storeName, 'readwrite');
            const store = tx.objectStore(storeName);
            const request = store.delete(id);
            
            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });
    }

    async clear(storeName) {
        return new Promise((resolve, reject) => {
            const tx = this.db.transaction(storeName, 'readwrite');
            const store = tx.objectStore(storeName);
            const request = store.clear();
            
            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });
    }

    async addToSyncQueue(action) {
        return this.save('syncQueue', {
            ...action,
            synced: 0,
            created_at: new Date().toISOString()
        });
    }

    async getUnsynced() {
        const items = await this.getAll('syncQueue');
        return items.filter(i => !i.synced);
    }

    async markSynced(id) {
        const item = await this.get('syncQueue', id);
        if (item) {
            item.synced = 1;
            await this.save('syncQueue', item);
        }
    }

    async cacheData(key, data, ttl = 3600000) {
        await this.save('cache', {
            key,
            data,
            expires: Date.now() + ttl
        });
    }

    async getCached(key) {
        const cached = await this.get('cache', key);
        if (cached && cached.expires > Date.now()) {
            return cached.data;
        }
        return null;
    }
}

const localDB = new LocalDB();