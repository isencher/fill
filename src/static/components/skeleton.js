/**
 * Loading Skeleton Components
 * Provides skeleton loading states for async content
 */

class SkeletonLoader {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error(`Skeleton container #${containerId} not found`);
            return;
        }

        this.options = {
            type: options.type || 'card', // card, list, table, text
            count: options.count || 3,
            animate: options.animate !== false,
            ...options
        };

        this.render();
    }

    render() {
        const animationClass = this.options.animate ? 'skeleton' : 'skeleton--static';
        let html = '';

        switch (this.options.type) {
            case 'card':
                html = this.renderCardSkeleton(animationClass);
                break;
            case 'list':
                html = this.renderListSkeleton(animationClass);
                break;
            case 'table':
                html = this.renderTableSkeleton(animationClass);
                break;
            case 'text':
                html = this.renderTextSkeleton(animationClass);
                break;
            default:
                html = this.renderCardSkeleton(animationClass);
        }

        this.container.innerHTML = html;
    }

    renderCardSkeleton(animationClass) {
        let cards = '';
        for (let i = 0; i < this.options.count; i++) {
            cards += `
                <div class="skeleton-card">
                    <div class="skeleton-card__header ${animationClass}"></div>
                    <div class="skeleton-card__title ${animationClass}"></div>
                    <div class="skeleton-card__body ${animationClass}"></div>
                    <div class="skeleton-card__body ${animationClass}"></div>
                    <div class="skeleton-card__body ${animationClass}"></div>
                </div>
            `;
        }
        return cards;
    }

    renderListSkeleton(animationClass) {
        let items = '';
        for (let i = 0; i < this.options.count; i++) {
            items += `
                <div class="skeleton-list-item">
                    <div class="skeleton-list-item__icon ${animationClass}"></div>
                    <div class="skeleton-list-item__content">
                        <div class="skeleton-list-item__title ${animationClass}"></div>
                        <div class="skeleton-list-item__subtitle ${animationClass}"></div>
                    </div>
                </div>
            `;
        }
        return items;
    }

    renderTableSkeleton(animationClass) {
        let rows = '';
        for (let i = 0; i < this.options.count; i++) {
            rows += `
                <div class="skeleton-table__row">
                    <div class="skeleton-table__cell ${animationClass}" style="width: 20%;"></div>
                    <div class="skeleton-table__cell ${animationClass}" style="width: 25%;"></div>
                    <div class="skeleton-table__cell ${animationClass}" style="width: 30%;"></div>
                    <div class="skeleton-table__cell ${animationClass}" style="width: 25%;"></div>
                </div>
            `;
        }
        return `
            <div class="skeleton-table__header ${animationClass}"></div>
            ${rows}
        `;
    }

    renderTextSkeleton(animationClass) {
        let lines = '';
        for (let i = 0; i < this.options.count; i++) {
            lines += `<div class="skeleton-text ${animationClass}"></div>`;
        }
        return lines;
    }

    destroy() {
        if (this.container) {
            this.container.innerHTML = '';
        }
    }
}

/**
 * Show skeleton loader in a container
 */
function showSkeleton(containerId, options = {}) {
    const container = document.getElementById(containerId);
    if (!container) {
        console.error(`Container #${containerId} not found`);
        return;
    }

    container.style.display = 'block';
    return new SkeletonLoader(containerId, options);
}

/**
 * Hide skeleton loader
 */
function hideSkeleton(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        container.style.display = 'none';
    }
}

/**
 * Helper function to show loading state with button animation
 */
function setButtonLoading(button, loading = true) {
    if (!button) return;

    if (loading) {
        button.classList.add('btn--loading');
        button.disabled = true;
    } else {
        button.classList.remove('btn--loading');
        button.disabled = false;
    }
}

/**
 * Helper function to show button success state
 */
function setButtonSuccess(button, duration = 1000) {
    if (!button) return;

    button.classList.add('btn--success');
    setTimeout(() => {
        button.classList.remove('btn--success');
    }, duration);
}

/**
 * Helper function to animate message display
 */
function animateMessage(messageElement, type = 'info') {
    if (!messageElement) return;

    // Remove existing animation classes
    messageElement.classList.remove('success', 'error', 'info');

    // Force reflow to restart animation
    void messageElement.offsetWidth;

    // Add new animation class
    messageElement.classList.add('show', type);

    // Auto-hide after 5 seconds
    setTimeout(() => {
        messageElement.classList.remove('show', type);
    }, 5000);
}

/**
 * Helper function to animate dropdown selection
 */
function animateSelectChange(selectElement) {
    if (!selectElement) return;

    // Remove and re-add animation class to restart it
    selectElement.classList.remove('select--changed');
    void selectElement.offsetWidth;
    selectElement.classList.add('select--changed');
}

/**
 * Predefined skeleton configurations
 */
const SkeletonConfigs = {
    TEMPLATE_LIST: {
        type: 'card',
        count: 6,
        animate: true
    },
    FILE_LIST: {
        type: 'list',
        count: 5,
        animate: true
    },
    DATA_PREVIEW: {
        type: 'table',
        count: 5,
        animate: true
    },
    PLACEHOLDER_LIST: {
        type: 'list',
        count: 4,
        animate: true
    },
    TEXT_CONTENT: {
        type: 'text',
        count: 3,
        animate: true
    }
};

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        SkeletonLoader,
        showSkeleton,
        hideSkeleton,
        setButtonLoading,
        setButtonSuccess,
        animateMessage,
        animateSelectChange,
        SkeletonConfigs
    };
}
