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
            } catch (error) {
                auth.clear();
            }
        }
        
        // Load appropriate page
        this.route();
        
        // Hide loading screen
        const loading = document.querySelector('.loading-screen');
        if (loading) {
            loading.style.display = 'none';
        }
    }

    route() {
        const path = window.location.pathname;
        const role = auth.getUserRole();
        
        // Handle root path
        if (path === '/' || path === '/index.html') {
            if (auth.isAuthenticated()) {
                auth.redirectBasedOnRole();
            } else {
                this.loadPage('/pages/landing.html');
            }
            return;
        }
        
        // Handle role-based redirects
        if (path.includes('/customer/') && role !== 'customer') {
            window.location.href = '/pages/login.html';
            return;
        }
        
        if (path.includes('/vendor/') && role !== 'vendor') {
            window.location.href = '/pages/login.html';
            return;
        }
        
        if (path.includes('/admin/') && role !== 'admin') {
            window.location.href = '/pages/admin/login.html';
            return;
        }
    }

    loadPage(pagePath) {
        // Load page content via fetch
        fetch(pagePath)
            .then(response => response.text())
            .then(html => {
                const app = document.getElementById('app');
                app.innerHTML = html;
                this.currentPage = pagePath;
                this.initializePage();
            })
            .catch(error => {
                console.error('Error loading page:', error);
                document.getElementById('app').innerHTML = `
                    <div class="loading-screen">
                        <p>Error loading page. Please try again.</p>
                        <button class="btn btn-primary" onclick="location.reload()">Retry</button>
                    </div>
                `;
            });
    }

    initializePage() {
        // Initialize page-specific scripts
        const pageName = this.currentPage.split('/').pop().replace('.html', '');
        
        // Dispatch page loaded event
        window.dispatchEvent(new CustomEvent('page-loaded', { 
            detail: { page: pageName } 
        }));
    }

    showToast(message, type = 'info') {
        // Simple toast notification
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            bottom: 24px;
            left: 50%;
            transform: translateX(-50%);
            background: ${type === 'error' ? '#dc2626' : '#0f5c2f'};
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

    showModal(title, content, actions = []) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal glass-card">
                <div class="modal-header">
                    <h3>${title}</h3>
                    <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">&times;</button>
                </div>
                <div class="modal-body">${content}</div>
                ${actions.length ? `
                    <div class="modal-actions">
                        ${actions.map(action => `
                            <button class="btn ${action.class || 'btn-secondary'}" onclick="${action.onClick}">${action.text}</button>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Close on overlay click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.remove();
        });
        
        return modal;
    }

    closeModal() {
        const modal = document.querySelector('.modal-overlay');
        if (modal) modal.remove();
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
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(8px);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
    }
    .modal {
        max-width: 500px;
        width: 90%;
        max-height: 80vh;
        overflow: auto;
    }
    .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }
    .modal-close {
        background: none;
        border: none;
        font-size: 24px;
        cursor: pointer;
        color: var(--text-secondary);
    }
    .modal-actions {
        display: flex;
        gap: 12px;
        justify-content: flex-end;
        margin-top: 24px;
    }
`;
document.head.appendChild(style);