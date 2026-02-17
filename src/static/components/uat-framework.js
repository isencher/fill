/**
 * User Acceptance Testing (UAT) Framework
 * Provides tools for collecting user feedback and running acceptance tests
 */

class UATFramework {
    constructor(options = {}) {
        this.sessionId = options.sessionId || this._generateSessionId();
        this.userId = options.userId || null;
        this.environment = options.environment || 'production';
        this.recording = options.recording || false;
        this.events = [];
        this.screenshots = [];
        this.startTime = Date.now();
        this.apiEndpoint = options.apiEndpoint || '/api/v1/uat';
    }

    /**
     * Generate unique session ID
     */
    _generateSessionId() {
        return `uat_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Start UAT session
     */
    start(scenario = {}) {
        console.log('[UAT] Starting session:', this.sessionId);

        this.recording = true;
        this.startTime = Date.now();

        this._recordEvent({
            type: 'session_start',
            timestamp: Date.now(),
            scenario: scenario.name,
            description: scenario.description
        });

        // Set up global event listeners
        this._setupEventListeners();

        return this.sessionId;
    }

    /**
     * Stop UAT session
     */
    stop() {
        console.log('[UAT] Stopping session:', this.sessionId);

        this.recording = false;

        this._recordEvent({
            type: 'session_end',
            timestamp: Date.now(),
            duration: Date.now() - this.startTime
        });

        this._teardownEventListeners();

        return this.getReport();
    }

    /**
     * Record user action
     */
    recordAction(action, details = {}) {
        if (!this.recording) {
            console.warn('[UAT] Not recording, session not started');
            return;
        }

        this._recordEvent({
            type: 'action',
            timestamp: Date.now(),
            action: action,
            details: details
        });
    }

    /**
     * Record user feedback
     */
    recordFeedback(feedback) {
        if (!this.recording) {
            console.warn('[UAT] Not recording, session not started');
            return;
        }

        this._recordEvent({
            type: 'feedback',
            timestamp: Date.now(),
            feedback: feedback
        });
    }

    /**
     * Record error
     */
    recordError(error, context = {}) {
        if (!this.recording) {
            console.warn('[UAT] Not recording, session not started');
            return;
        }

        this._recordEvent({
            type: 'error',
            timestamp: Date.now(),
            error: {
                message: error.message,
                stack: error.stack,
                name: error.name
            },
            context: context
        });
    }

    /**
     * Record performance metrics
     */
    recordPerformance(metric, value) {
        if (!this.recording) {
            console.warn('[UAT] Not recording, session not started');
            return;
        }

        this._recordEvent({
            type: 'performance',
            timestamp: Date.now(),
            metric: metric,
            value: value
        });
    }

    /**
     * Take screenshot
     */
    async takeScreenshot(label = '') {
        // This would integrate with a screenshot service
        // For now, just record the intent
        this._recordEvent({
            type: 'screenshot',
            timestamp: Date.now(),
            label: label
        });

        console.log('[UAT] Screenshot:', label);
    }

    /**
     * Record event
     */
    _recordEvent(event) {
        event.sessionId = this.sessionId;
        event.userId = this.userId;
        this.events.push(event);
        console.log('[UAT] Event:', event.type);
    }

    /**
     * Setup event listeners
     */
    _setupEventListeners() {
        // Listen for clicks
        this.clickHandler = (e) => {
            const target = e.target;
            this.recordAction('click', {
                tagName: target.tagName,
                id: target.id,
                className: target.className,
                text: target.textContent?.substring(0, 50),
                href: target.href
            });
        };

        // Listen for navigation
        this.popstateHandler = () => {
            this.recordAction('navigation', {
                url: window.location.href
            });
        };

        // Listen for errors
        this.errorHandler = (e) => {
            this.recordError(e.error || new Error(e.message), {
                filename: e.filename,
                lineno: e.lineno,
                colno: e.colno
            });
        };

        // Listen for unhandled rejections
        this.rejectionHandler = (e) => {
            this.recordError(e.reason || new Error('Unhandled Promise Rejection'), {
                type: 'unhandledrejection'
            });
        };

        document.addEventListener('click', this.clickHandler, true);
        window.addEventListener('popstate', this.popstateHandler);
        window.addEventListener('error', this.errorHandler);
        window.addEventListener('unhandledrejection', this.rejectionHandler);
    }

    /**
     * Teardown event listeners
     */
    _teardownEventListeners() {
        document.removeEventListener('click', this.clickHandler, true);
        window.removeEventListener('popstate', this.popstateHandler);
        window.removeEventListener('error', this.errorHandler);
        window.removeEventListener('unhandledrejection', this.rejectionHandler);
    }

    /**
     * Get session report
     */
    getReport() {
        const duration = Date.now() - this.startTime;

        return {
            sessionId: this.sessionId,
            userId: this.userId,
            environment: this.environment,
            startTime: this.startTime,
            endTime: Date.now(),
            duration: duration,
            eventCount: this.events.length,
            events: this.events,
            summary: this._generateSummary()
        };
    }

    /**
     * Generate summary
     */
    _generateSummary() {
        const summary = {
            actions: 0,
            feedbacks: 0,
            errors: 0,
            performanceMetrics: 0,
            screenshots: 0
        };

        this.events.forEach(event => {
            switch (event.type) {
                case 'action':
                    summary.actions++;
                    break;
                case 'feedback':
                    summary.feedbacks++;
                    break;
                case 'error':
                    summary.errors++;
                    break;
                case 'performance':
                    summary.performanceMetrics++;
                    break;
                case 'screenshot':
                    summary.screenshots++;
                    break;
            }
        });

        return summary;
    }

    /**
     * Upload report to server
     */
    async uploadReport() {
        const report = this.getReport();

        try {
            const response = await fetch(this.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(report)
            });

            if (!response.ok) {
                throw new Error(`Upload failed: ${response.statusText}`);
            }

            const result = await response.json();
            console.log('[UAT] Report uploaded:', result);
            return result;
        } catch (error) {
            console.error('[UAT] Upload error:', error);
            throw error;
        }
    }

    /**
     * Export report as JSON
     */
    exportReport() {
        const report = this.getReport();
        const json = JSON.stringify(report, null, 2);
        const blob = new Blob([json], { type: 'application/json' });
        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = `uat_report_${this.sessionId}.json`;
        a.click();

        URL.revokeObjectURL(url);
        console.log('[UAT] Report exported');
    }

    /**
     * Show feedback modal
     */
    showFeedbackModal(options = {}) {
        const modal = document.createElement('div');
        modal.className = 'uat-feedback-modal';
        modal.innerHTML = `
            <div class="uat-feedback-content">
                <h3>${options.title || 'Share Your Feedback'}</h3>
                <p>${options.message || 'Please help us improve by sharing your experience.'}</p>
                <div class="uat-feedback-form">
                    <div class="uat-rating">
                        <label>How was your experience?</label>
                        <div class="uat-stars" data-rating="0">
                            <span class="star" data-value="1">★</span>
                            <span class="star" data-value="2">★</span>
                            <span class="star" data-value="3">★</span>
                            <span class="star" data-value="4">★</span>
                            <span class="star" data-value="5">★</span>
                        </div>
                    </div>
                    <div class="uat-comments">
                        <label for="feedback">Comments (optional)</label>
                        <textarea id="feedback" rows="4" placeholder="Tell us more about your experience..."></textarea>
                    </div>
                    <div class="uat-email">
                        <label for="email">Email (optional)</label>
                        <input type="email" id="email" placeholder="your@email.com">
                    </div>
                    <div class="uat-actions">
                        <button type="button" class="uat-submit">Submit Feedback</button>
                        <button type="button" class="uat-cancel">Cancel</button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Set up star rating
        const stars = modal.querySelectorAll('.star');
        const ratingContainer = modal.querySelector('.uat-stars');
        let rating = 0;

        stars.forEach(star => {
            star.addEventListener('click', () => {
                rating = parseInt(star.dataset.value);
                ratingContainer.dataset.rating = rating;
                stars.forEach((s, index) => {
                    s.classList.toggle('active', index < rating);
                });
            });
        });

        // Set up submit
        const submitBtn = modal.querySelector('.uat-submit');
        const cancelBtn = modal.querySelector('.uat-cancel');

        submitBtn.addEventListener('click', () => {
            const feedback = {
                rating: rating,
                comments: modal.querySelector('#feedback').value,
                email: modal.querySelector('#email').value,
                timestamp: Date.now()
            };

            this.recordFeedback(feedback);
            modal.remove();
            options.onSubmit?.(feedback);
        });

        cancelBtn.addEventListener('click', () => {
            modal.remove();
            options.onCancel?.();
        });

        return modal;
    }

    /**
     * Run test scenario
     */
    async runScenario(scenario) {
        console.log('[UAT] Running scenario:', scenario.name);

        this.start({
            name: scenario.name,
            description: scenario.description
        });

        try {
            await scenario.execute(this);
            console.log('[UAT] Scenario completed:', scenario.name);
        } catch (error) {
            console.error('[UAT] Scenario failed:', scenario.name, error);
            this.recordError(error, { scenario: scenario.name });
        }

        return this.stop();
    }

    /**
     * Create predefined scenarios
     */
    static scenarios = {
        uploadFile: {
            name: 'Upload File',
            description: 'User uploads a data file',
            execute: async (uat) => {
                // Guide user to upload file
                uat.showFeedbackModal({
                    title: 'Upload File Test',
                    message: 'Please upload a test file (CSV or Excel) and verify the upload was successful.'
                });
            }
        },

        selectTemplate: {
            name: 'Select Template',
            description: 'User selects a template for their data',
            execute: async (uat) => {
                uat.showFeedbackModal({
                    title: 'Template Selection Test',
                    message: 'Please select a template from the list and verify it matches your expectations.'
                });
            }
        },

        configureMapping: {
            name: 'Configure Mapping',
            description: 'User configures column-to-placeholder mappings',
            execute: async (uat) => {
                uat.showFeedbackModal({
                    title: 'Mapping Configuration Test',
                    message: 'Please configure the mappings between your data columns and template placeholders. Is the mapping interface clear?'
                });
            }
        },

        downloadResults: {
            name: 'Download Results',
            description: 'User downloads generated documents',
            execute: async (uat) => {
                uat.showFeedbackModal({
                    title: 'Download Test',
                    message: 'Please download the generated documents and verify they are correct.'
                });
            }
        },

        completeWorkflow: {
            name: 'Complete Workflow',
            description: 'User completes the entire workflow from upload to download',
            execute: async (uat) => {
                uat.showFeedbackModal({
                    title: 'Complete Workflow Test',
                    message: 'Please complete the full workflow: upload file, select template, configure mapping, and download results. Share your overall experience.'
                });
            }
        }
    };
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UATFramework;
}

// Create singleton instance
const uat = new UATFramework();
