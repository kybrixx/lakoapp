// Chat System for Lako
class ChatManager {
    constructor() {
        this.socket = null;
        this.currentConversation = null;
        this.messages = [];
        this.typingTimeout = null;
        this.listeners = [];
        this.unreadCount = 0;
    }

    connect() {
        const token = api.getToken();
        if (!token) return;
        
        this.socket = io(API_BASE.replace('/api', ''), {
            transports: ['websocket'],
            auth: { token }
        });
        
        this.socket.on('connect', () => {
            console.log('Chat connected');
            this.notifyListeners('connected');
        });
        
        this.socket.on('disconnect', () => {
            console.log('Chat disconnected');
            this.notifyListeners('disconnected');
        });
        
        this.socket.on('message', (data) => {
            this.handleIncomingMessage(data);
        });
        
        this.socket.on('typing', (data) => {
            this.notifyListeners('typing', data);
        });
        
        this.socket.on('message_read', (data) => {
            this.notifyListeners('read', data);
        });
    }

    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
        }
    }

    joinConversation(userId) {
        if (this.socket) {
            this.socket.emit('join', { user_id: userId });
            this.currentConversation = userId;
        }
    }

    leaveConversation() {
        if (this.socket && this.currentConversation) {
            this.socket.emit('leave', { user_id: this.currentConversation });
            this.currentConversation = null;
        }
    }

    sendMessage(receiverId, message, images = null) {
        return new Promise((resolve, reject) => {
            if (!this.socket) {
                reject(new Error('Chat not connected'));
                return;
            }
            
            const messageData = {
                receiver_id: receiverId,
                message,
                images,
                timestamp: new Date().toISOString()
            };
            
            this.socket.emit('message', messageData);
            
            // Also save via API for persistence
            api.sendMessage(receiverId, message, images)
                .then(resolve)
                .catch(reject);
        });
    }

    sendTyping(receiverId, isTyping) {
        if (this.socket) {
            this.socket.emit('typing', {
                receiver_id: receiverId,
                typing: isTyping
            });
        }
    }

    markAsRead(senderId) {
        if (this.socket) {
            this.socket.emit('read', { sender_id: senderId });
        }
        api.request(`/chat/mark-read/${senderId}`, { method: 'POST' });
    }

    handleIncomingMessage(data) {
        this.messages.push(data);
        
        if (data.sender_id !== auth.getUser()?.id) {
            this.unreadCount++;
        }
        
        this.notifyListeners('message', data);
        
        // Show notification if not in chat
        if (window.location.pathname.indexOf('/chat') === -1) {
            this.showNotification(data);
        }
    }

    showNotification(data) {
        if (Notification.permission === 'granted') {
            new Notification('New Message', {
                body: data.message || 'Sent you a message',
                icon: '/assets/images/logo.png'
            });
        }
    }

    async loadConversations() {
        try {
            return await api.getConversations();
        } catch (error) {
            console.error('Error loading conversations:', error);
            return { conversations: [] };
        }
    }

    async loadMessages(userId, limit = 50) {
        try {
            const data = await api.getMessages(userId);
            this.messages = data.messages || [];
            return this.messages;
        } catch (error) {
            console.error('Error loading messages:', error);
            return [];
        }
    }

    on(event, callback) {
        this.listeners.push({ event, callback });
    }

    off(event, callback) {
        this.listeners = this.listeners.filter(l => 
            !(l.event === event && l.callback === callback)
        );
    }

    notifyListeners(event, data) {
        this.listeners
            .filter(l => l.event === event)
            .forEach(l => l.callback(data));
    }

    getUnreadCount() {
        return this.unreadCount;
    }

    resetUnreadCount() {
        this.unreadCount = 0;
    }

    requestNotificationPermission() {
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }
    }

    formatMessageTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        
        if (diff < 86400000) {
            return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        } else if (diff < 604800000) {
            return date.toLocaleDateString([], { weekday: 'short' });
        } else {
            return date.toLocaleDateString();
        }
    }

    groupMessagesByDate(messages) {
        const groups = {};
        messages.forEach(msg => {
            const date = new Date(msg.created_at).toLocaleDateString();
            if (!groups[date]) groups[date] = [];
            groups[date].push(msg);
        });
        return groups;
    }
}

const chatManager = new ChatManager();

// Initialize chat when authenticated
if (auth.isAuthenticated()) {
    chatManager.connect();
    chatManager.requestNotificationPermission();
}