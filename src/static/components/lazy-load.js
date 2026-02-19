/**
 * Lazy Loading Utility Component
 * Provides lazy loading functionality for lists and grids
 */

class LazyLoader {
    constructor(options = {}) {
        this.itemsPerPage = options.itemsPerPage || 20;
        this.loadMoreThreshold = options.loadMoreThreshold || 200; // px from bottom
        this.currentPage = 0;
        this.totalItems = 0;
        this.loadedItems = [];
        this.isLoading = false;
        this.hasMore = true;
        this.onLoadMore = options.onLoadMore || null;
        this.container = options.container || null;
        this.renderItem = options.renderItem || null;
    }

    /**
     * Initialize lazy loading
     */
    init() {
        if (!this.container) {
            console.error('LazyLoader: container is required');
            return;
        }

        // Add scroll listener
        this.container.addEventListener('scroll', this._handleScroll.bind(this));

        // For window scroll
        window.addEventListener('scroll', this._handleScroll.bind(this));

        // Initial load
        this.loadMore();
    }

    /**
     * Handle scroll events
     */
    _handleScroll() {
        if (this.isLoading || !this.hasMore) {
            return;
        }

        const scrollPosition = this._getScrollPosition();
        const scrollHeight = this._getScrollHeight();
        const offsetHeight = this._getOffsetHeight();

        // Check if user is near bottom
        if (scrollPosition + offsetHeight >= scrollHeight - this.loadMoreThreshold) {
            this.loadMore();
        }
    }

    /**
     * Get current scroll position
     */
    _getScrollPosition() {
        if (this.container) {
            return this.container.scrollTop;
        }
        return window.pageYOffset || document.documentElement.scrollTop;
    }

    /**
     * Get total scroll height
     */
    _getScrollHeight() {
        if (this.container) {
            return this.container.scrollHeight;
        }
        return Math.max(
            document.body.scrollHeight,
            document.documentElement.scrollHeight,
            document.body.offsetHeight,
            document.documentElement.offsetHeight,
            document.body.clientHeight,
            document.documentElement.clientHeight
        );
    }

    /**
     * Get offset height
     */
    _getOffsetHeight() {
        if (this.container) {
            return this.container.offsetHeight;
        }
        return window.innerHeight;
    }

    /**
     * Load more items
     */
    async loadMore() {
        if (this.isLoading || !this.hasMore) {
            return;
        }

        this.isLoading = true;
        this._showLoadingIndicator();

        try {
            const newItems = await this.onLoadMore(this.currentPage, this.itemsPerPage);

            if (newItems && newItems.length > 0) {
                this.loadedItems.push(...newItems);
                this.currentPage++;
                this.totalItems = this.loadedItems.length;

                // Check if there are more items
                if (newItems.length < this.itemsPerPage) {
                    this.hasMore = false;
                }

                // Render new items
                this._renderItems(newItems);

                // Hide loading indicator
                this._hideLoadingIndicator();

                // Show "Load More" button if there's more content
                if (this.hasMore) {
                    this._showLoadMoreButton();
                }
            } else {
                this.hasMore = false;
                this._hideLoadingIndicator();
            }
        } catch (error) {
            console.error('Error loading more items:', error);
            this._showErrorIndicator();
        } finally {
            this.isLoading = false;
        }
    }

    /**
     * Render items to container
     */
    _renderItems(items) {
        if (!this.renderItem) {
            console.error('LazyLoader: renderItem function is required');
            return;
        }

        const targetContainer = this.container !== window ? this.container : document.body;

        // Find or create items container
        let itemsContainer = targetContainer.querySelector('[data-lazy-items]');
        if (!itemsContainer) {
            itemsContainer = document.createElement('div');
            itemsContainer.setAttribute('data-lazy-items', '');
            targetContainer.appendChild(itemsContainer);
        }

        // Render each item
        items.forEach(item => {
            const itemElement = this.renderItem(item);
            itemsContainer.appendChild(itemElement);
        });
    }

    /**
     * Show loading indicator
     */
    _showLoadingIndicator() {
        const targetContainer = this.container !== window ? this.container : document.body;

        // Remove existing indicator
        this._hideLoadingIndicator();

        // Create loading indicator
        const loadingIndicator = document.createElement('div');
        loadingIndicator.setAttribute('data-lazy-loading', '');
        loadingIndicator.className = 'lazy-loading-indicator';
        loadingIndicator.innerHTML = `
            <div class="lazy-loading-spinner"></div>
            <div class="lazy-loading-text">加载中...</div>
        `;

        targetContainer.appendChild(loadingIndicator);
    }

    /**
     * Hide loading indicator
     */
    _hideLoadingIndicator() {
        const existing = document.querySelector('[data-lazy-loading]');
        if (existing) {
            existing.remove();
        }
    }

    /**
     * Show error indicator
     */
    _showErrorIndicator() {
        const targetContainer = this.container !== window ? this.container : document.body;

        this._hideLoadingIndicator();

        const errorIndicator = document.createElement('div');
        errorIndicator.setAttribute('data-lazy-error', '');
        errorIndicator.className = 'lazy-error-indicator';
        errorIndicator.innerHTML = `
            <div class="lazy-error-message">加载失败，请重试</div>
            <button class="lazy-retry-btn">重试</button>
        `;

        const retryBtn = errorIndicator.querySelector('.lazy-retry-btn');
        retryBtn.addEventListener('click', () => {
            errorIndicator.remove();
            this.loadMore();
        });

        targetContainer.appendChild(errorIndicator);
    }

    /**
     * Show "Load More" button
     */
    _showLoadMoreButton() {
        const targetContainer = this.container !== window ? this.container : document.body;

        // Remove existing button
        this._hideLoadMoreButton();

        const loadMoreBtn = document.createElement('button');
        loadMoreBtn.setAttribute('data-lazy-load-more', '');
        loadMoreBtn.className = 'lazy-load-more-btn btn-secondary';
        loadMoreBtn.textContent = '加载更多';
        loadMoreBtn.addEventListener('click', () => {
            this.loadMore();
        });

        targetContainer.appendChild(loadMoreBtn);
    }

    /**
     * Hide "Load More" button
     */
    _hideLoadMoreButton() {
        const existing = document.querySelector('[data-lazy-load-more]');
        if (existing) {
            existing.remove();
        }
    }

    /**
     * Reset lazy loader state
     */
    reset() {
        this.currentPage = 0;
        this.totalItems = 0;
        this.loadedItems = [];
        this.isLoading = false;
        this.hasMore = true;

        // Clear container
        const itemsContainer = document.querySelector('[data-lazy-items]');
        if (itemsContainer) {
            itemsContainer.innerHTML = '';
        }

        // Hide indicators
        this._hideLoadingIndicator();
        this._hideLoadMoreButton();
    }

    /**
     * Destroy lazy loader
     */
    destroy() {
        if (this.container) {
            this.container.removeEventListener('scroll', this._handleScroll);
        }
        window.removeEventListener('scroll', this._handleScroll);

        this._hideLoadingIndicator();
        this._hideLoadMoreButton();

        const itemsContainer = document.querySelector('[data-lazy-items]');
        if (itemsContainer) {
            itemsContainer.remove();
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LazyLoader;
}
