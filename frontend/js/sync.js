// Sync Service for Offline-First Operations
class SyncService {
    constructor() {
        this.isOnline = navigator.onLine;
        this.syncInProgress = false;
        this.listeners = [];
        this.init();
    }

    init() {
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.notifyListeners('online');
        });
        
        window.addEventListener('offline', () => {
            this.isOnline = false;
            this.notifyListeners('offline');
        });
    }

    onStatusChange(callback) {
        this.listeners.push(callback);
    }

    notifyListeners(status) {
        this.listeners.forEach(cb => cb(status));
    }

    async sync() {
        if (!this.isOnline || this.syncInProgress) return;
        
        this.syncInProgress = true;
        showToast('Syncing data...', 'info', 2000);
        
        try {
            // Pull changes from server
            await this.pullChanges();
            
            // Push local changes to server
            await this.pushChanges();
            
            showToast('Sync complete', 'success', 2000);
        } catch (error) {
            console.error('Sync error:', error);
            showToast('Sync failed', 'error');
        } finally {
            this.syncInProgress = false;
        }
    }

    async pullChanges() {
        try {
            const data = await api.pullChanges();
            
            for (const [table, records] of Object.entries(data.changes || {})) {
                if (records.length) {
                    await localDB.save(table, records);
                }
            }
        } catch (error) {
            console.error('Pull error:', error);
            throw error;
        }
    }

    async pushChanges() {
        const unsynced = await localDB.getUnsynced();
        if (!unsynced.length) return;
        
        try {
            await api.pushChanges(unsynced);
            
            for (const item of unsynced) {
                await localDB.markSynced(item.id);
            }
        } catch (error) {
            console.error('Push error:', error);
            throw error;
        }
    }

    async queueAction(action, data) {
        await localDB.addToSyncQueue({ action, data });
        if (this.isOnline) {
            this.sync();
        }
    }

    startPeriodicSync(intervalMs = 300000) {
        setInterval(() => {
            if (this.isOnline) {
                this.sync();
            }
        }, intervalMs);
    }
}

const syncService = new SyncService();
syncService.startPeriodicSync();