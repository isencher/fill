/**
 * Undo/Redo Manager for Mappings
 * Manages mapping state history with undo/redo support
 */

class UndoRedoManager {
    constructor(options = {}) {
        this.maxHistory = options.maxHistory || 50;
        this.history = [];
        this.currentIndex = -1;
        this.autoSaveKey = options.autoSaveKey || 'mapping_draft';
        this.onStateChange = options.onStateChange || null;
        this.autoSave = options.autoSave !== false;

        // Load from localStorage if available
        this._loadFromStorage();

        // Listen for beforeunload to save draft
        window.addEventListener('beforeunload', this._handleBeforeUnload.bind(this));
    }

    /**
     * Add new state to history
     */
    pushState(state, description = '') {
        // Remove any future states if we're not at the end
        if (this.currentIndex < this.history.length - 1) {
            this.history = this.history.slice(0, this.currentIndex + 1);
        }

        // Add new state
        this.history.push({
            state: state,
            description: description,
            timestamp: new Date().toISOString()
        });

        // Limit history size
        if (this.history.length > this.maxHistory) {
            this.history.shift();
        } else {
            this.currentIndex++;
        }

        // Auto-save to localStorage
        if (this.autoSave) {
            this._saveToStorage();
        }

        // Notify state change
        if (this.onStateChange) {
            this.onStateChange({
                canUndo: this.canUndo(),
                canRedo: this.canRedo(),
                currentIndex: this.currentIndex,
                historyLength: this.history.length,
                description: description
            });
        }

        return this.currentIndex;
    }

    /**
     * Undo to previous state
     */
    undo() {
        if (!this.canUndo()) {
            console.warn('[UndoRedo] Cannot undo - already at oldest state');
            return null;
        }

        this.currentIndex--;

        const stateInfo = this.history[this.currentIndex];

        // Auto-save after undo
        if (this.autoSave) {
            this._saveToStorage();
        }

        // Notify state change
        if (this.onStateChange) {
            this.onStateChange({
                action: 'undo',
                canUndo: this.canUndo(),
                canRedo: this.canRedo(),
                currentIndex: this.currentIndex,
                description: `Undo: ${stateInfo.description}`
            });
        }

        console.log(`[UndoRedo] Undo to ${stateInfo.description}`);

        return stateInfo.state;
    }

    /**
     * Redo to next state
     */
    redo() {
        if (!this.canRedo()) {
            console.warn('[UndoRedo] Cannot redo - already at newest state');
            return null;
        }

        this.currentIndex++;

        const stateInfo = this.history[this.currentIndex];

        // Auto-save after redo
        if (this.autoSave) {
            this._saveToStorage();
        }

        // Notify state change
        if (this.onStateChange) {
            this.onStateChange({
                action: 'redo',
                canUndo: this.canUndo(),
                canRedo: this.canRedo(),
                currentIndex: this.currentIndex,
                description: `Redo: ${stateInfo.description}`
            });
        }

        console.log(`[UndoRedo] Redo to ${stateInfo.description}`);

        return stateInfo.state;
    }

    /**
     * Check if undo is available
     */
    canUndo() {
        return this.currentIndex > 0;
    }

    /**
     * Check if redo is available
     */
    canRedo() {
        return this.currentIndex < this.history.length - 1;
    }

    /**
     * Get current state
     */
    getCurrentState() {
        if (this.currentIndex === -1) {
            return null;
        }

        return this.history[this.currentIndex].state;
    }

    /**
     * Reset to initial state
     */
    reset() {
        this.history = [];
        this.currentIndex = -1;

        this._clearStorage();

        if (this.onStateChange) {
            this.onStateChange({
                action: 'reset',
                canUndo: false,
                canRedo: false,
                currentIndex: -1,
                historyLength: 0
            });
        }

        console.log('[UndoRedo] Reset to initial state');
    }

    /**
     * Get history info
     */
    getHistoryInfo() {
        return {
            currentIndex: this.currentIndex,
            historyLength: this.history.length,
            canUndo: this.canUndo(),
            canRedo: this.canRedo(),
            history: this.history.map((item, index) => ({
                index: index,
                description: item.description,
                timestamp: item.timestamp,
                isCurrent: index === this.currentIndex
            }))
        };
    }

    /**
     * Save draft to localStorage
     */
    _saveToStorage() {
        try {
            const data = {
                history: this.history,
                currentIndex: this.currentIndex,
                savedAt: new Date().toISOString()
            };
            localStorage.setItem(this.autoSaveKey, JSON.stringify(data));
        } catch (error) {
            console.error('[UndoRedo] Failed to save to localStorage:', error);
        }
    }

    /**
     * Load draft from localStorage
     */
    _loadFromStorage() {
        try {
            const data = localStorage.getItem(this.autoSaveKey);
            if (!data) {
                console.log('[UndoRedo] No saved draft found');
                return;
            }

            const parsed = JSON.parse(data);

            if (parsed.history && Array.isArray(parsed.history) && parsed.history.length > 0) {
                this.history = parsed.history;
                this.currentIndex = parsed.currentIndex || 0;

                console.log(`[UndoRedo] Loaded ${this.history.length} states from storage`);
            }
        } catch (error) {
            console.error('[UndoRedo] Failed to load from localStorage:', error);
        }
    }

    /**
     * Clear saved draft from localStorage
     */
    _clearStorage() {
        try {
            localStorage.removeItem(this.autoSaveKey);
        } catch (error) {
            console.error('[UndoRedo] Failed to clear localStorage:', error);
        }
    }

    /**
     * Handle beforeunload event
     */
    _handleBeforeUnload(event) {
        if (this.autoSave && this.history.length > 0) {
            this._saveToStorage();
        }
    }

    /**
     * Destroy undo/redo manager
     */
    destroy() {
        window.removeEventListener('beforeunload', this._handleBeforeUnload);
        this.reset();
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UndoRedoManager;
}
