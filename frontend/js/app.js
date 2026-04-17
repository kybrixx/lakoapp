// Main Application Controller
class App {
    constructor() {
        this.currentPage = null;
        this.init();
    }

    async init() {
        // Check authentication
        if (auth.isAuthenticated()) {
            try {
                await api.getCurrentUser();
                // Redirect to dashboard if on landing page
                if (window.location.pathname === '/' || window.location.pathname === '/index.html') {
                    auth.redirectBasedOnRole();
                    return;
                }
            } catch (error) {
                auth.clear();
            }
        }
        
        // Hide loading screen
        const loading = document.querySelector('.loading-screen');
        if (loading) {
            loading.style.display = 'none';
        }
        
        this.route();
    }

    route() {
        const path = window.location.pathname;
        const role = auth.getUserRole();
        
        // Handle root path
        if (path === '/' || path === '/index.html') {
            if (auth.isAuthenticated()) {
                auth.redirectBasedOnRole();
            }
            // Landing page already loaded by index.html
            return;
        }
        
        // Handle role-based redirects
        if (path.includes('/customer/') && role !== 'customer' && role !== 'admin') {
            window.location.href = '/pages/login.html';
            return;
        }
        
        if (path.includes('/vendor/') && role !== 'vendor' && role !== 'admin') {
            window.location.href = '/pages/login.html';
            return;
        }
        
        if (path.includes('/admin/') && role !== 'admin') {
            window.location.href = '/pages/admin/login.html';
            return;
        }
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            bottom: 24px;
            left: 50%;
            transform: translateX(-50%);
            background: ${type === 'error' ? '#dc2626' : type === 'success' ? '#10b981' : '#0f5c2f'};
            color: white;
            padding: 12px 24px;
            border-radius: 40px;
            font-size: 14px;
            font-weight: 500;
            z-index: 9999;
            animation: slideUp 0.3s ease;
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideDown 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new App();
});

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideUp {
        from { opacity: 0; transform: translateX(-50%) translateY(20px); }
        to { opacity: 1; transform: translateX(-50%) translateY(0); }
    }
    @keyframes slideDown {
        from { opacity: 1; transform: translateX(-50%) translateY(0); }
        to { opacity: 0; transform: translateX(-50%) translateY(20px); }
    }
`;
document.head.appendChild(style);