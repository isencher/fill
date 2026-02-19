/**
 * Service Worker Manager
 * Registers and manages the service worker
 */

class ServiceWorkerManager {
    constructor() {
        this.registration = null;
        this.isOnline = navigator.onLine;
        this.offlineIndicator = null;
    }

    /**
     * Register the service worker
     */
    async register() {
        if (!('serviceWorker' in navigator)) {
            console.warn('[Service Worker] Not supported in this browser');
            return false;
        }

        try {
            // Register service worker
            this.registration = await navigator.serviceWorker.register('/static/service-worker.js', {
                scope: '/'
            });

            console.log('[Service Worker] Registered:', this.registration.scope);

            // Wait for service worker to be ready
            await navigator.serviceWorker.ready;
            console.log('[Service Worker] Ready');

            // Set up message listener
            this._setupMessageListener();

            // Set up online/offline listeners
            this._setupConnectivityListeners();

            // Show offline indicator if needed
            this._updateOnlineStatus();

            return true;
        } catch (error) {
            console.error('[Service Worker] Registration failed:', error);
            return false;
        }
    }

    /**
     * Set up message listener for communication with service worker
     */
    _setupMessageListener() {
        navigator.serviceWorker.addEventListener('message', (event) => {
            const { data } = event;

            switch (data.type) {
                case 'CACHE_SIZE':
                    console.log('[Service Worker] Cache size:', data);
                    break;
                default:
                    console.log('[Service Worker] Message:', data);
            }
        });
    }

    /**
     * Set up online/offline connectivity listeners
     */
    _setupConnectivityListeners() {
        window.addEventListener('online', () => {
            this.isOnline = true;
            this._updateOnlineStatus();
            this._showNotification('网络已连接', 'success');
        });

        window.addEventListener('offline', () => {
            this.isOnline = false;
            this._updateOnlineStatus();
            this._showNotification('网络已断开，使用离线模式', 'warning');
        });
    }

    /**
     * Update online status indicator
     */
    _updateOnlineStatus() {
        // Remove existing indicator
        if (this.offlineIndicator) {
            this.offlineIndicator.remove();
            this.offlineIndicator = null;
        }

        if (!this.isOnline) {
            this._showOfflineIndicator();
        }

        // Update body class
        if (this.isOnline) {
            document.body.classList.remove('offline');
            document.body.classList.add('online');
        } else {
            document.body.classList.remove('online');
            document.body.classList.add('offline');
        }
    }

    /**
     * Show offline indicator
     */
    _showOfflineIndicator() {
        // Don't show if already showing
        if (document.querySelector('.offline-indicator')) {
            return;
        }

        const indicator = document.createElement('div');
        indicator.className = 'offline-indicator';
        indicator.innerHTML = `
            <span class="offline-icon">⚠️</span>
            <span class="offline-text">离线模式</span>
        `;

        document.body.appendChild(indicator);
        this.offlineIndicator = indicator;
    }

    /**
     * Show notification
     */
    _showNotification(message, type = 'info') {
        // Remove existing notification
        const existing = document.querySelector('.sw-notification');
        if (existing) {
            existing.remove();
        }

        const notification = document.createElement('div');
        notification.className = `sw-notification sw-notification-${type}`;
        notification.textContent = message;

        document.body.appendChild(notification);

        // Auto-remove after 3 seconds
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    /**
     * Get cache size
     */
    async getCacheSize() {
        if (!this.registration) {
            return null;
        }

        return new Promise((resolve) => {
            const messageChannel = new MessageChannel();

            messageChannel.port1.onmessage = (event) => {
                resolve(event.data);
            };

            this.registration.active.postMessage({
                type: 'GET_CACHE_SIZE'
            }, [messageChannel.port2]);
        });
    }

    /**
     * Clear all caches
     */
    async clearCache() {
        if (!this.registration) {
            return false;
        }

        this.registration.active.postMessage({
            type: 'CLEAR_CACHE'
        });

        return true;
    }

    /**
     * Skip waiting and activate new service worker
     */
    async skipWaiting() {
        if (!this.registration) {
            return false;
        }

        if (this.registration.waiting) {
            this.registration.waiting.postMessage({
                type: 'SKIP_WAITING'
            });

            // Reload page to activate new service worker
            window.location.reload();
            return true;
        }

        return false;
    }

    /**
     * Check for updates
     */
    async checkForUpdates() {
        if (!this.registration) {
            return false;
        }

        await this.registration.update();

        return this.registration.waiting !== null;
    }
}

// Create singleton instance
const swManager = new ServiceWorkerManager();

// Register service worker on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        swManager.register();
    });
} else {
    swManager.register();
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ServiceWorkerManager;
}
