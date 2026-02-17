/**
 * Global Progress Indicator Component
 * Shows the 4-step workflow: Upload → Template → Mapping → Download
 */

class ProgressIndicator {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error(`Progress container #${containerId} not found`);
            return;
        }

        // Steps configuration
        this.steps = [
            { id: 'upload', label: 'Upload', icon: '📁', url: '/' },
            { id: 'template', label: 'Template', icon: '📄', url: '/templates.html' },
            { id: 'mapping', label: 'Mapping', icon: '🔗', url: '/mapping.html' },
            { id: 'download', label: 'Download', icon: '⬇️', url: '/download.html' }
        ];

        this.currentStep = options.currentStep || this.detectCurrentStep();
        this.completedSteps = options.completedSteps || [];
        this.onClick = options.onClick || null;

        this.render();
    }

    /**
     * Detect current step based on URL path
     */
    detectCurrentStep() {
        const path = window.location.pathname;

        if (path === '/' || path.includes('index')) return 'upload';
        if (path.includes('template')) return 'template';
        if (path.includes('mapping')) return 'mapping';
        if (path.includes('download')) return 'download';

        return 'upload'; // default
    }

    /**
     * Render the progress indicator
     */
    render() {
        const progressHtml = `
            <div class="progress-indicator">
                ${this.steps.map((step, index) => this.renderStep(step, index)).join('')}
            </div>
        `;

        this.container.innerHTML = progressHtml;
        this.attachEventListeners();
    }

    /**
     * Render a single step
     */
    renderStep(step, index) {
        const isCompleted = this.completedSteps.includes(step.id) || index < this.steps.findIndex(s => s.id === this.currentStep);
        const isActive = step.id === this.currentStep;
        const isPending = !isCompleted && !isActive;

        const statusClass = isCompleted ? 'completed' : (isActive ? 'active' : 'pending');

        return `
            <div class="progress-step ${statusClass}" data-step="${step.id}">
                <div class="step-icon">
                    ${isCompleted ? '✓' : step.icon}
                </div>
                <div class="step-label">${step.label}</div>
                ${index < this.steps.length - 1 ? '<div class="step-connector"></div>' : ''}
            </div>
        `;
    }

    /**
     * Attach click event listeners to steps
     */
    attachEventListeners() {
        if (!this.onClick) return;

        const steps = this.container.querySelectorAll('.progress-step');
        steps.forEach(step => {
            step.addEventListener('click', () => {
                const stepId = step.dataset.step;
                this.onClick(stepId);
            });
        });
    }

    /**
     * Update the current step
     */
    setCurrentStep(stepId) {
        if (!this.steps.find(s => s.id === stepId)) {
            console.warn(`Invalid step ID: ${stepId}`);
            return;
        }

        this.currentStep = stepId;
        this.render();
    }

    /**
     * Mark a step as completed
     */
    markCompleted(stepId) {
        if (!this.completedSteps.includes(stepId)) {
            this.completedSteps.push(stepId);
        }
        this.render();
    }

    /**
     * Mark multiple steps as completed
     */
    markCompletedMultiple(stepIds) {
        stepIds.forEach(stepId => {
            if (!this.completedSteps.includes(stepId)) {
                this.completedSteps.push(stepId);
            }
        });
        this.render();
    }

    /**
     * Reset all completed steps
     */
    resetCompleted() {
        this.completedSteps = [];
        this.render();
    }

    /**
     * Get step information
     */
    getStepInfo(stepId) {
        return this.steps.find(s => s.id === stepId);
    }

    /**
     * Navigate to a specific step
     */
    navigateToStep(stepId) {
        const step = this.getStepInfo(stepId);
        if (step && step.url) {
            window.location.href = step.url;
        }
    }
}

/**
 * Initialize progress indicator on page load
 */
function initProgressIndicator(options = {}) {
    // Look for a container with id "progressContainer" or create one
    let container = document.getElementById('progressContainer');

    if (!container) {
        // Try to find a header or create container at top of body
        const header = document.querySelector('.header');
        if (header) {
            container = document.createElement('div');
            container.id = 'progressContainer';
            header.appendChild(container);
        } else {
            // Create container at the beginning of body
            container = document.createElement('div');
            container.id = 'progressContainer';
            document.body.insertBefore(container, document.body.firstChild);
        }
    }

    return new ProgressIndicator('progressContainer', options);
}

// Auto-initialize if container exists
if (document.getElementById('progressContainer')) {
    initProgressIndicator();
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ProgressIndicator, initProgressIndicator };
}
