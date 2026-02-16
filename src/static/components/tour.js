/**
 * Tour Component
 * Provides interactive guided tours for first-time users
 */

class Tour {
    constructor(options = {}) {
        this.steps = options.steps || [];
        this.currentStep = 0;
        this.onComplete = options.onComplete || (() => {});
        this.onSkip = options.onSkip || (() => {});

        this.overlay = null;
        this.tooltip = null;
        this.isActive = false;
        this.currentElement = null;
    }

    createElements() {
        // Create overlay
        this.overlay = document.createElement('div');
        this.overlay.className = 'tour-overlay';

        // Create tooltip
        this.tooltip = document.createElement('div');
        this.tooltip.className = 'tour-tooltip';
        this.tooltip.innerHTML = `
            <div class="tour-tooltip-header">
                <h3 class="tour-tooltip-title"></h3>
                <button class="tour-tooltip-close" aria-label="Close tour">&times;</button>
            </div>
            <div class="tour-tooltip-content"></div>
            <div class="tour-tooltip-footer">
                <span class="tour-tooltip-steps"></span>
                <div class="tour-tooltip-buttons">
                    <button class="tour-tooltip-skip">Skip</button>
                    <button class="tour-tooltip-prev" style="display: none;">Back</button>
                    <button class="tour-tooltip-next">Next</button>
                </div>
            </div>
        `;

        // Event listeners
        this.tooltip.querySelector('.tour-tooltip-close').addEventListener('click', () => this.end('skipped'));
        this.tooltip.querySelector('.tour-tooltip-skip').addEventListener('click', () => this.end('skipped'));
        this.tooltip.querySelector('.tour-tooltip-prev').addEventListener('click', () => this.previous());
        this.tooltip.querySelector('.tour-tooltip-next').addEventListener('click', () => this.next());

        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (!this.isActive) return;

            if (e.key === 'Escape') {
                this.end('skipped');
            } else if (e.key === 'ArrowRight') {
                this.next();
            } else if (e.key === 'ArrowLeft') {
                this.previous();
            }
        });

        document.body.appendChild(this.overlay);
        document.body.appendChild(this.tooltip);
    }

    start() {
        if (this.steps.length === 0) return;

        this.createElements();
        this.isActive = true;
        this.currentStep = 0;
        this.showStep(this.currentStep);
    }

    showStep(index) {
        if (index < 0 || index >= this.steps.length) {
            this.end('completed');
            return;
        }

        const step = this.steps[index];
        this.currentStep = index;

        // Remove previous highlight
        if (this.currentElement) {
            this.currentElement.classList.remove('tour-highlight', 'pulse');
        }

        // Find target element
        const target = document.querySelector(step.target);
        if (!target) {
            console.warn(`Tour target not found: ${step.target}`);
            this.next();
            return;
        }

        this.currentElement = target;
        target.classList.add('tour-highlight', 'pulse');

        // Scroll target into view
        target.scrollIntoView({ behavior: 'smooth', block: 'center' });

        // Update tooltip content
        const title = this.tooltip.querySelector('.tour-tooltip-title');
        const content = this.tooltip.querySelector('.tour-tooltip-content');
        const steps = this.tooltip.querySelector('.tour-tooltip-steps');
        const prevBtn = this.tooltip.querySelector('.tour-tooltip-prev');
        const nextBtn = this.tooltip.querySelector('.tour-tooltip-next');
        const skipBtn = this.tooltip.querySelector('.tour-tooltip-skip');

        title.textContent = step.title || '';
        content.innerHTML = step.content || '';
        steps.textContent = `${index + 1} of ${this.steps.length}`;

        // Update buttons
        prevBtn.style.display = index === 0 ? 'none' : 'block';
        nextBtn.textContent = index === this.steps.length - 1 ? 'Finish' : 'Next';
        skipBtn.style.display = index === this.steps.length - 1 ? 'none' : 'block';

        // Position tooltip
        this.positionTooltip(target);

        // Show overlay and tooltip
        this.overlay.classList.add('show');
        this.tooltip.classList.add('show');

        // Handle window resize
        window.addEventListener('resize', () => this.positionTooltip(target), { once: true });
    }

    positionTooltip(target) {
        if (!this.tooltip || !target) return;

        const targetRect = target.getBoundingClientRect();
        const tooltipRect = this.tooltip.getBoundingClientRect();
        const padding = 20;

        // Calculate position
        let top, left;

        // Try to position above first, then below if needed
        if (targetRect.top - tooltipRect.height - padding > 0) {
            // Position above
            top = targetRect.top - tooltipRect.height - padding;
            left = targetRect.left + (targetRect.width - tooltipRect.width) / 2;
        } else if (targetRect.bottom + tooltipRect.height + padding < window.innerHeight) {
            // Position below
            top = targetRect.bottom + padding;
            left = targetRect.left + (targetRect.width - tooltipRect.width) / 2;
        } else {
            // Center in viewport
            top = (window.innerHeight - tooltipRect.height) / 2;
            left = (window.innerWidth - tooltipRect.width) / 2;
        }

        // Keep tooltip within viewport
        left = Math.max(padding, Math.min(left, window.innerWidth - tooltipRect.width - padding));
        top = Math.max(padding, Math.min(top, window.innerHeight - tooltipRect.height - padding));

        this.tooltip.style.top = `${top}px`;
        this.tooltip.style.left = `${left}px`;
    }

    next() {
        this.showStep(this.currentStep + 1);
    }

    previous() {
        this.showStep(this.currentStep - 1);
    }

    end(reason) {
        // Remove highlight
        if (this.currentElement) {
            this.currentElement.classList.remove('tour-highlight', 'pulse');
        }

        // Hide overlay and tooltip
        this.overlay.classList.remove('show');
        this.tooltip.classList.remove('show');

        // Remove from DOM after animation
        setTimeout(() => {
            if (this.overlay) {
                this.overlay.remove();
                this.overlay = null;
            }
            if (this.tooltip) {
                this.tooltip.remove();
                this.tooltip = null;
            }
        }, 300);

        this.isActive = false;

        // Call callbacks
        if (reason === 'completed') {
            this.onComplete();
        } else {
            this.onSkip();
        }
    }

    // Check if tour has been shown before
    static hasBeenShown(tourId) {
        return localStorage.getItem(`tour_${tourId}_completed`) === 'true';
    }

    // Mark tour as shown
    static markAsShown(tourId) {
        localStorage.setItem(`tour_${tourId}_completed`, 'true');
    }

    // Reset tour (for testing)
    static reset(tourId) {
        localStorage.removeItem(`tour_${tourId}_completed`);
    }
}

// Page-specific tour definitions
const TOURS = {
    upload: {
        steps: [
            {
                target: '.upload-area',
                title: '📤 Upload Your Data',
                content: 'Start by uploading your Excel or CSV file. You can drag and drop or click to browse.',
            },
            {
                target: '#continueBtn',
                title: '➡️ Continue to Templates',
                content: 'After uploading, click Continue to select a template for your data.',
            },
        ],
    },
    templates: {
        steps: [
            {
                target: '.template-grid',
                title: '📄 Choose a Template',
                content: 'Select a pre-built template or upload your own custom template.',
            },
            {
                target: '[data-testid="use-template-btn"]',
                title: '✨ Use Template',
                content: 'Click "Use Template" to proceed to the mapping step.',
            },
        ],
    },
    mapping: {
        steps: [
            {
                target: '.auto-match-btn',
                title: '✨ Auto-Match Fields',
                content: 'Click Auto-Match to let the system automatically map your data columns to template placeholders.',
            },
            {
                target: '.placeholder-select',
                title: '🔗 Manual Mapping',
                content: 'If auto-match isn\'t perfect, you can manually select the correct column for each field.',
            },
            {
                target: '#saveMappingBtn',
                title: '💾 Save and Process',
                content: 'When ready, click Save & Process to generate your documents.',
            },
        ],
    },
};

// Auto-start tour if not shown before
function autoStartTour(pageName) {
    const tourConfig = TOURS[pageName];
    if (!tourConfig) return;

    const tourId = `${pageName}_tour`;

    if (!Tour.hasBeenShown(tourId)) {
        // Show tour after a short delay
        setTimeout(() => {
            const tour = new Tour({
                steps: tourConfig.steps,
                onComplete: () => {
                    Tour.markAsShown(tourId);
                },
                onSkip: () => {
                    // Mark as shown even if skipped
                    Tour.markAsShown(tourId);
                },
            });

            tour.start();
        }, 1000);
    }
}

// Export for use in pages
window.Tour = Tour;
window.autoStartTour = autoStartTour;
window.TOURS = TOURS;
