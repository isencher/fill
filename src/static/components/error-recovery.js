/**
 * Error Recovery and Retry Mechanism
 * Handles error recovery, auto-save, and retry logic
 */

class ErrorRecovery {
    constructor(options = {}) {
        this.maxRetries = options.maxRetries || 3;
        this.retryDelay = options.retryDelay || 1000;
        this.onRetry = options.onRetry || null;
        this.onRecovery = options.onRecovery || null;
        this.onFailure = options.onFailure || null;
    }

    /**
     * Retry function with exponential backoff
     */
    async retry(fn, context = 'operation') {
        let lastError = null;

        for (let attempt = 1; attempt <= this.maxRetries; attempt++) {
            try {
                const result = await fn();

                // Success - log recovery if this was a retry
                if (attempt > 1) {
                    console.log(`[ErrorRecovery] ${context} succeeded on attempt ${attempt}`);

                    if (this.onRecovery) {
                        this.onRecovery({
                            context: context,
                            attempt: attempt,
                            lastError: lastError
                        });
                    }
                }

                return result;
            } catch (error) {
                lastError = error;
                console.error(`[ErrorRecovery] ${context} failed on attempt ${attempt}:`, error);

                // Check if error is retryable
                if (!this._isRetryableError(error)) {
                    console.error(`[ErrorRecovery] ${context} error is not retryable`);
                    throw error;
                }

                // Wait before retrying (exponential backoff)
                const delay = this.retryDelay * Math.pow(2, attempt - 1);

                if (attempt < this.maxRetries) {
                    console.log(`[ErrorRecovery] Retrying ${context} in ${delay}ms...`);

                    if (this.onRetry) {
                        this.onRetry({
                            context: context,
                            attempt: attempt,
                            maxRetries: this.maxRetries,
                            delay: delay,
                            error: error
                        });
                    }

                    await this._sleep(delay);
                }
            }
        }

        // All retries failed
        console.error(`[ErrorRecovery] ${context} failed after ${this.maxRetries} attempts`);

        if (this.onFailure) {
            this.onFailure({
                context: context,
                maxRetries: this.maxRetries,
                lastError: lastError
            });
        }

        throw lastError;
    }

    /**
     * Check if error is retryable
     */
    _isRetryableError(error) {
        // Network errors
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            return true;
        }

        // Timeout errors
        if (error.name === 'AbortError' || error.message?.includes('timeout')) {
            return true;
        }

        // Server errors (5xx)
        if (error.status >= 500 && error.status < 600) {
            return true;
        }

        // Rate limiting (429)
        if (error.status === 429) {
            return true;
        }

        return false;
    }

    /**
     * Sleep for specified milliseconds
     */
    _sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Safe fetch with retry
     */
    async safeFetch(url, options = {}, retryContext = 'fetch') {
        return this.retry(async () => {
            const response = await fetch(url, options);

            if (!response.ok) {
                const error = new Error(`HTTP ${response.status}: ${response.statusText}`);
                error.status = response.status;
                error.response = response;
                throw error;
            }

            return response;
        }, retryContext);
    }

    /**
     * Save draft to localStorage
     */
    saveDraft(key, data) {
        try {
            const draft = {
                data: data,
                timestamp: new Date().toISOString(),
                version: 1
            };

            localStorage.setItem(key, JSON.stringify(draft));

            console.log(`[ErrorRecovery] Draft saved: ${key}`);

            return {
                success: true,
                key: key
            };
        } catch (error) {
            console.error('[ErrorRecovery] Failed to save draft:', error);

            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Load draft from localStorage
     */
    loadDraft(key) {
        try {
            const data = localStorage.getItem(key);

            if (!data) {
                return {
                    found: false,
                    key: key
                };
            }

            const draft = JSON.parse(data);

            console.log(`[ErrorRecovery] Draft loaded: ${key}`);

            return {
                found: true,
                key: key,
                draft: draft
            };
        } catch (error) {
            console.error('[ErrorRecovery] Failed to load draft:', error);

            return {
                found: false,
                key: key,
                error: error.message
            };
        }
    }

    /**
     * Delete draft from localStorage
     */
    deleteDraft(key) {
        try {
            localStorage.removeItem(key);

            console.log(`[ErrorRecovery] Draft deleted: ${key}`);

            return {
                success: true,
                key: key
            };
        } catch (error) {
            console.error('[ErrorRecovery] Failed to delete draft:', error);

            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Check if there's an auto-saved draft
     */
    hasDraft(key) {
        const result = this.loadDraft(key);
        return result.found;
    }

    /**
     * Clear all drafts
     */
    clearAllDrafts(prefix = 'draft_') {
        try {
            const keys = Object.keys(localStorage);

            let cleared = 0;

            keys.forEach(key => {
                if (key.startsWith(prefix)) {
                    localStorage.removeItem(key);
                    cleared++;
                }
            });

            console.log(`[ErrorRecovery] Cleared ${cleared} drafts`);

            return {
                success: true,
                cleared: cleared
            };
        } catch (error) {
            console.error('[ErrorRecovery] Failed to clear drafts:', error);

            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Recover from error with user action
     */
    async recoverWithErrorPrompt(error, context = 'operation') {
        console.log(`[ErrorRecovery] Attempting to recover from error in ${context}`);

        // Check if there's a draft we can restore
        const draftKey = `${context}_draft`;
        const draft = this.loadDraft(draftKey);

        if (draft.found) {
            const shouldRestore = confirm(`We found an unsaved draft for ${context}. Would you like to restore it?`);

            if (shouldRestore) {
                console.log(`[ErrorRecovery] Restoring draft for ${context}`);
                return draft.draft.data;
            }
        }

        // Check if user wants to retry
        const shouldRetry = confirm(`The operation failed: ${error.message}. Would you like to retry?`);

        if (shouldRetry) {
            console.log(`[ErrorRecovery] Retrying ${context} after user confirmation`);
            return {
                shouldRetry: true
            };
        }

        return {
            shouldRetry: false,
            recovered: false
        };
    }

    /**
     * Detect if file was updated after upload
     */
    detectFileUpdate(originalFile, currentFile) {
        if (!originalFile || !currentFile) {
            return {
                updated: false,
                reason: 'No files to compare'
            };
        }

        // Check if file was modified
        if (originalFile.lastModified !== currentFile.lastModified) {
            return {
                updated: true,
                reason: 'File was modified',
                originalModified: originalFile.lastModified,
                currentModified: currentFile.lastModified
            };
        }

        // Check if file size changed
        if (originalFile.size !== currentFile.size) {
            return {
                updated: true,
                reason: 'File size changed',
                originalSize: originalFile.size,
                currentSize: currentFile.size
            };
        }

        return {
            updated: false
        };
    }

    /**
     * Detect if template was modified
     */
    detectTemplateModification(originalTemplate, currentTemplate) {
        if (!originalTemplate || !currentTemplate) {
            return {
                modified: false,
                reason: 'No templates to compare'
            };
        }

        // Compare template content
        const originalContent = JSON.stringify(originalTemplate);
        const currentContent = JSON.stringify(currentTemplate);

        if (originalContent !== currentContent) {
            return {
                modified: true,
                reason: 'Template content changed'
            };
        }

        return {
            modified: false
        };
    }

    /**
     * Resolve conflict with user choice
     */
    async resolveConflict(conflictInfo) {
        const message = `Conflict detected: ${conflictInfo.reason}

Options:
1. Keep current version (${conflictInfo.current})
2. Restore original version (${conflictInfo.original})
3. Merge both versions

What would you like to do?`;

        // In a real app, this would show a modal dialog
        const choice = confirm(`${message}\n\nClick OK to keep current, Cancel to restore original.`);

        return {
            action: choice ? 'keep' : 'restore',
            conflictInfo: conflictInfo
        };
    }

    /**
     * Auto-recover on page reload
     */
    autoRecover(context) {
        console.log(`[ErrorRecovery] Checking for auto-recovery for ${context}`);

        const draftKey = `${context}_draft`;
        const draft = this.loadDraft(draftKey);

        if (draft.found) {
            // Check if draft is recent (within 24 hours)
            const draftTime = new Date(draft.draft.timestamp);
            const now = new Date();
            const hoursSinceSave = (now - draftTime) / (1000 * 60 * 60);

            if (hoursSinceSave < 24) {
                console.log(`[ErrorRecovery] Found recent draft (${hoursSinceSave.toFixed(1)} hours old)`);

                // Show recovery notification
                if (window.Notification && Notification.permission === 'granted') {
                    new Notification('Draft Found', {
                        body: 'We found an unsaved draft. Would you like to restore it?',
                        icon: '/static/icons/draft.png'
                    });
                }

                return draft;
            }
        }

        return null;
    }

    /**
     * Create retry button UI
     */
    createRetryButton(options = {}) {
        const button = document.createElement('button');
        button.className = 'retry-btn';
        button.innerHTML = `
            <span class="retry-icon">🔄</span>
            <span class="retry-text">Retry</span>
        `;
        button.setAttribute('aria-label', options.label || 'Retry failed operation');
        button.setAttribute('type', 'button');

        button.addEventListener('click', async (e) => {
            e.preventDefault();

            button.classList.add('retrying');
            button.disabled = true;

            const retryText = button.querySelector('.retry-text');
            if (retryText) {
                retryText.textContent = 'Retrying...';
            }

            try {
                if (options.onRetry) {
                    await options.onRetry();
                }
            } catch (error) {
                console.error('[ErrorRecovery] Retry failed:', error);

                button.classList.remove('retrying');
                button.disabled = false;

                const retryText = button.querySelector('.retry-text');
                if (retryText) {
                    retryText.textContent = 'Retry Failed';
                }

                setTimeout(() => {
                    if (retryText) {
                        retryText.textContent = 'Retry';
                    }
                    button.classList.remove('retrying');
                    button.disabled = false;
                }, 2000);
            }
        });

        return button;
    }

    /**
     * Create save draft button UI
     */
    createSaveDraftButton(options = {}) {
        const button = document.createElement('button');
        button.className = 'save-draft-btn btn-secondary';
        button.innerHTML = `
            <span class="save-icon">💾</span>
            <span class="save-text">Save Draft</span>
        `;
        button.setAttribute('aria-label', 'Save current work as draft');
        button.setAttribute('type', 'button');

        button.addEventListener('click', async (e) => {
            e.preventDefault();

            button.classList.add('saving');
            button.disabled = true;

            const saveText = button.querySelector('.save-text');
            if (saveText) {
                saveText.textContent = 'Saving...';
            }

            try {
                if (options.onSave) {
                    const result = await options.onSave();

                    if (result.success) {
                        button.classList.remove('saving');
                        button.classList.add('saved');

                        const saveText = button.querySelector('.save-text');
                        if (saveText) {
                            saveText.textContent = 'Saved!';
                        }

                        setTimeout(() => {
                            button.classList.remove('saved');
                            button.disabled = false;

                            if (saveText) {
                                saveText.textContent = 'Save Draft';
                            }
                        }, 2000);
                    }
                }
            } catch (error) {
                console.error('[ErrorRecovery] Failed to save draft:', error);

                button.classList.remove('saving');
                button.disabled = false;

                const saveText = button.querySelector('.save-text');
                if (saveText) {
                    saveText.textContent = 'Save Failed';
                }

                setTimeout(() => {
                    if (saveText) {
                        saveText.textContent = 'Save Draft';
                    }
                    button.classList.remove('failed');
                }, 2000);
            }
        });

        return button;
    }
}

// Create singleton instance
const errorRecovery = new ErrorRecovery();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ErrorRecovery;
}
