/**
 * Empty State Component
 * Provides consistent empty state UI across all pages
 *
 * Usage:
 *   const emptyState = new EmptyState('containerId', {
 *     icon: '📁',
 *     title: 'No files uploaded',
 *     message: 'Upload a file to get started',
 *     actions: [
 *       { label: 'Upload File', onClick: () => {...}, primary: true }
 *     ]
 *   });
 */

class EmptyState {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error(`EmptyState container #${containerId} not found`);
            return;
        }

        this.options = {
            icon: options.icon || '📭',
            title: options.title || 'No data available',
            message: options.message || '',
            actions: options.actions || [],
            size: options.size || 'medium', // small, medium, large
            variant: options.variant || 'default', // default, info, warning, error
            ...options
        };

        this.render();
    }

    /**
     * Render the empty state component
     */
    render() {
        const sizeClass = `empty-state--${this.options.size}`;
        const variantClass = `empty-state--${this.options.variant}`;

        const html = `
            <div class="empty-state ${sizeClass} ${variantClass}">
                <div class="empty-state__icon">${this.options.icon}</div>
                <div class="empty-state__content">
                    <h3 class="empty-state__title">${this.options.title}</h3>
                    ${this.options.message ? `<p class="empty-state__message">${this.options.message}</p>` : ''}
                </div>
                ${this.renderActions()}
            </div>
        `;

        this.container.innerHTML = html;
        this.attachEventListeners();
    }

    /**
     * Render action buttons
     */
    renderActions() {
        if (!this.options.actions || this.options.actions.length === 0) {
            return '';
        }

        const buttons = this.options.actions.map(action => {
            const buttonClass = action.primary
                ? 'empty-state__button--primary'
                : 'empty-state__button--secondary';

            return `
                <button
                    class="empty-state__button ${buttonClass}"
                    data-action="${action.label}"
                    ${action.disabled ? 'disabled' : ''}
                >
                    ${action.icon ? `<span class="empty-state__button-icon">${action.icon}</span>` : ''}
                    ${action.label}
                </button>
            `;
        }).join('');

        return `<div class="empty-state__actions">${buttons}</div>`;
    }

    /**
     * Attach click event listeners to action buttons
     */
    attachEventListeners() {
        const buttons = this.container.querySelectorAll('.empty-state__button');
        buttons.forEach(button => {
            button.addEventListener('click', () => {
                const actionLabel = button.dataset.action;
                const action = this.options.actions.find(a => a.label === actionLabel);
                if (action && action.onClick) {
                    action.onClick();
                }
            });
        });
    }

    /**
     * Update the empty state content
     */
    update(options) {
        this.options = { ...this.options, ...options };
        this.render();
    }

    /**
     * Show the empty state
     */
    show() {
        this.container.style.display = 'block';
    }

    /**
     * Hide the empty state
     */
    hide() {
        this.container.style.display = 'none';
    }

    /**
     * Destroy the component
     */
    destroy() {
        if (this.container) {
            this.container.innerHTML = '';
        }
    }
}

/**
 * Predefined empty state configurations
 */
const EmptyStates = {
    // Upload page empty states
    NO_FILES_UPLOADED: {
        icon: '📁',
        title: 'No files uploaded yet',
        message: 'Upload a CSV or Excel file to get started with data filling',
        actions: [
            { label: 'Choose File', primary: true }
        ]
    },

    // Template page empty states
    NO_TEMPLATES_AVAILABLE: {
        icon: '📄',
        title: 'No templates available',
        message: 'Create a template or upload one to get started',
        actions: [
            { label: 'Upload Template', primary: true },
            { label: 'Create New', primary: false }
        ]
    },

    NO_DATA_FILE: {
        icon: '⚠️',
        title: 'No data file uploaded',
        message: 'Please upload a data file before selecting a template',
        variant: 'warning',
        actions: [
            { label: '← Back to Upload', primary: true }
        ]
    },

    // Mapping page empty states
    NO_FILE_OR_TEMPLATE: {
        icon: '🔗',
        title: 'Setup required',
        message: 'Please upload a data file and select a template to configure column mappings',
        actions: [
            { label: 'Upload File', primary: false },
            { label: 'Select Template', primary: false }
        ]
    },

    NO_COLUMNS_TO_MAP: {
        icon: '📊',
        title: 'No columns to map',
        message: 'The uploaded file has no columns or the template has no placeholders',
        variant: 'info',
        actions: []
    },

    // Error states
    ERROR_LOADING_DATA: {
        icon: '❌',
        title: 'Failed to load data',
        message: 'There was an error loading the requested data. Please try again.',
        variant: 'error',
        actions: [
            { label: 'Retry', primary: true },
            { label: 'Go Back', primary: false }
        ]
    },

    FILE_NOT_FOUND: {
        icon: '🔍',
        title: 'File not found',
        message: 'The requested file could not be found. It may have been deleted.',
        variant: 'error',
        actions: [
            { label: 'Upload New File', primary: true }
        ]
    },

    TEMPLATE_NOT_FOUND: {
        icon: '🔍',
        title: 'Template not found',
        message: 'The requested template could not be found. It may have been deleted.',
        variant: 'error',
        actions: [
            { label: 'Select Another Template', primary: true }
        ]
    }
};

/**
 * Convenience function to create an empty state
 */
function createEmptyState(containerId, config) {
    // If config is a string, look it up in predefined states
    if (typeof config === 'string') {
        const predefined = EmptyStates[config];
        if (!predefined) {
            console.warn(`Empty state "${config}" not found, using default`);
            return new EmptyState(containerId);
        }
        return new EmptyState(containerId, predefined);
    }

    // Otherwise, use the provided config
    return new EmptyState(containerId, config);
}

/**
 * Show an empty state in a container
 */
function showEmptyState(containerId, config) {
    const container = document.getElementById(containerId);
    if (!container) {
        console.error(`Container #${containerId} not found`);
        return;
    }

    container.style.display = 'block';
    return createEmptyState(containerId, config);
}

/**
 * Hide an empty state container
 */
function hideEmptyState(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        container.style.display = 'none';
    }
}

// Auto-export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        EmptyState,
        EmptyStates,
        createEmptyState,
        showEmptyState,
        hideEmptyState
    };
}
