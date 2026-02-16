/**
 * Keyboard Navigation Manager
 * Handles keyboard navigation and focus management
 */

class KeyboardNavManager {
    constructor() {
        this.focusStack = [];
        this.currentTrap = null;
        this.trapCleanup = null;
        this.lastFocusedElement = null;
    }

    /**
     * Initialize keyboard navigation
     */
    init() {
        // Track focus changes
        document.addEventListener('focusin', this._handleFocusIn.bind(this));

        // Handle ESC key globally
        document.addEventListener('keydown', this._handleGlobalKeydown.bind(this));

        // Set up initial tab order
        this._setupTabOrder();

        // Make all interactive elements focusable
        this._makeInteractiveFocusable();

        console.log('[KeyboardNav] Initialized');
    }

    /**
     * Handle focus in event
     */
    _handleFocusIn(event) {
        // Store last focused element before modal/dialog opens
        if (!event.target.closest('[role="dialog"]') &&
            !event.target.closest('.modal') &&
            !event.target.closest('[aria-modal="true"]')) {
            this.lastFocusedElement = event.target;
        }
    }

    /**
     * Handle global keyboard events
     */
    _handleGlobalKeydown(event) {
        // ESC key - close modals or return to last element
        if (event.key === 'Escape') {
            if (this.currentTrap) {
                this.releaseFocusTrap();
            }
        }
    }

    /**
     * Set up logical tab order
     */
    _setupTabOrder() {
        // Find all interactive elements
        const interactiveElements = document.querySelectorAll(
            'a, button, input, select, textarea, [tabindex]:not([tabindex="-1"]), [role="button"]'
        );

        // Set appropriate tab indices if not already set
        interactiveElements.forEach((element, index) => {
            if (!element.hasAttribute('tabindex')) {
                // Only add tabindex to elements that are naturally focusable
                const naturallyFocusable = element.matches(
                    'a[href], button, input:not([type="hidden"]), select, textarea, [tabindex]'
                );

                if (!naturallyFocusable && element.getAttribute('role') === 'button') {
                    // Make div/button-like elements focusable
                    element.setAttribute('tabindex', '0');
                }
            }
        });
    }

    /**
     * Make interactive elements focusable
     */
    _makeInteractiveFocusable() {
        // Make elements with role="button" focusable and keyboard-interactive
        const buttonLikeElements = document.querySelectorAll('[role="button"]:not([tabindex])');
        buttonLikeElements.forEach(element => {
            element.setAttribute('tabindex', '0');

            // Add keyboard activation
            element.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    element.click();
                }
            });
        });

        // Make card-like elements focusable
        const cardElements = document.querySelectorAll('.template-card:not([tabindex])');
        cardElements.forEach(element => {
            element.setAttribute('tabindex', '0');
            element.setAttribute('role', 'button');

            // Add keyboard activation
            element.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    // Find the use-template button and click it
                    const useButton = element.querySelector('.use-template-btn');
                    if (useButton) {
                        useButton.click();
                    } else {
                        element.click();
                    }
                }
            });
        });

        // Make dropdown containers navigable
        const dropdowns = document.querySelectorAll('.dropdown, select');
        dropdowns.forEach(dropdown => {
            dropdown.addEventListener('keydown', (e) => {
                const options = dropdown.querySelectorAll('option, [role="option"]');
                const currentIndex = Array.from(options).indexOf(document.activeElement);

                switch (e.key) {
                    case 'ArrowUp':
                        e.preventDefault();
                        if (currentIndex > 0) {
                            options[currentIndex - 1].focus();
                        }
                        break;
                    case 'ArrowDown':
                        e.preventDefault();
                        if (currentIndex < options.length - 1) {
                            options[currentIndex + 1].focus();
                        }
                        break;
                    case 'Home':
                        e.preventDefault();
                        if (options.length > 0) {
                            options[0].focus();
                        }
                        break;
                    case 'End':
                        e.preventDefault();
                        if (options.length > 0) {
                            options[options.length - 1].focus();
                        }
                        break;
                }
            });
        });
    }

    /**
     * Trap focus within a container (for modals, dialogs)
     */
    trapFocus(container) {
        if (this.currentTrap) {
            console.warn('[KeyboardNav] Focus already trapped');
            return;
        }

        this.currentTrap = container;

        // Get all focusable elements within container
        const focusableElements = container.querySelectorAll(
            'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"]), [role="button"]'
        );

        if (focusableElements.length === 0) {
            console.warn('[KeyboardNav] No focusable elements in container');
            return;
        }

        const firstFocusable = focusableElements[0];
        const lastFocusable = focusableElements[focusableElements.length - 1];

        // Store last focused element before trap
        this.lastFocusedElement = document.activeElement;

        // Focus first element
        setTimeout(() => {
            firstFocusable.focus();
        }, 100);

        // Handle Tab key
        this.trapCleanup = this._trapFocusHandler(container, firstFocusable, lastFocusable);

        console.log('[KeyboardNav] Focus trapped in container', container);
    }

    /**
     * Focus trap handler
     */
    _trapFocusHandler(container, firstElement, lastElement) {
        const handleKeyDown = (e) => {
            if (e.key !== 'Tab') return;

            if (e.shiftKey) {
                // Shift + Tab
                if (document.activeElement === firstElement) {
                    e.preventDefault();
                    lastElement.focus();
                }
            } else {
                // Tab
                if (document.activeElement === lastElement) {
                    e.preventDefault();
                    firstElement.focus();
                }
            }
        };

        container.addEventListener('keydown', handleKeyDown);

        // Return cleanup function
        return () => {
            container.removeEventListener('keydown', handleKeyDown);
        };
    }

    /**
     * Release focus trap
     */
    releaseFocusTrap() {
        if (!this.currentTrap) {
            return;
        }

        // Clean up event listener
        if (this.trapCleanup) {
            this.trapCleanup();
            this.trapCleanup = null;
        }

        // Return focus to last element before trap
        if (this.lastFocusedElement && this.lastFocusedElement !== document.body) {
            this.lastFocusedElement.focus();
        }

        this.currentTrap = null;
        console.log('[KeyboardNav] Focus trap released');
    }

    /**
     * Move focus to next element
     */
    moveFocus(forward = true) {
        const focusableElements = Array.from(document.querySelectorAll(
            'a[href]:not([hidden]), button:not([hidden]):not([disabled]), input:not([hidden]):not([disabled]), select:not([hidden]):not([disabled]), textarea:not([hidden]):not([disabled]), [tabindex="0"]:not([hidden]), [role="button"]:not([hidden])'
        ));

        const currentIndex = focusableElements.indexOf(document.activeElement);

        let nextIndex;
        if (forward) {
            nextIndex = (currentIndex + 1) % focusableElements.length;
        } else {
            nextIndex = currentIndex <= 0 ? focusableElements.length - 1 : currentIndex - 1;
        }

        if (focusableElements[nextIndex]) {
            focusableElements[nextIndex].focus();
        }
    }

    /**
     * Jump to specific element by id
     */
    jumpTo(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.scrollIntoView({ behavior: 'smooth', block: 'center' });
            setTimeout(() => {
                element.focus();
            }, 300);
        }
    }

    /**
     * Add keyboard shortcuts
     */
    addShortcuts(shortcuts) {
        document.addEventListener('keydown', (e) => {
            // Check for modifier keys
            if (e.ctrlKey || e.metaKey || e.altKey) {
                Object.entries(shortcuts).forEach(([key, handler]) => {
                    if (this._matchShortcut(e, key)) {
                        e.preventDefault();
                        handler(e);
                    }
                });
            } else {
                // Regular shortcuts
                Object.entries(shortcuts).forEach(([key, handler]) => {
                    if (this._matchShortcut(e, key)) {
                        e.preventDefault();
                        handler(e);
                    }
                });
            }
        });
    }

    /**
     * Match keyboard event to shortcut
     */
    _matchShortcut(event, shortcut) {
        const parts = shortcut.split('+');
        const key = parts.pop().toLowerCase();
        const modifiers = parts;

        // Check modifiers
        for (const mod of modifiers) {
            if (mod === 'ctrl' && !event.ctrlKey) return false;
            if (mod === 'alt' && !event.altKey) return false;
            if (mod === 'shift' && !event.shiftKey) return false;
            if (mod === 'meta' && !event.metaKey) return false;
        }

        // Check key
        return event.key.toLowerCase() === key;
    }

    /**
     * Announce to screen readers
     */
    announce(message, priority = 'polite') {
        // Use A11yUtils announce if available
        if (window.A11yUtils && A11yUtils.announce) {
            A11yUtils.announce(message, priority);
        } else {
            // Fallback: create live region
            const announcer = document.createElement('div');
            announcer.setAttribute('role', 'status');
            announcer.setAttribute('aria-live', priority);
            announcer.setAttribute('aria-atomic', 'true');
            announcer.className = 'sr-only';
            announcer.textContent = message;

            document.body.appendChild(announcer);

            setTimeout(() => {
                announcer.remove();
            }, 1000);
        }
    }

    /**
     * Destroy keyboard navigation manager
     */
    destroy() {
        if (this.trapCleanup) {
            this.trapCleanup();
        }

        document.removeEventListener('focusin', this._handleFocusIn);
        document.removeEventListener('keydown', this._handleGlobalKeydown);

        console.log('[KeyboardNav] Destroyed');
    }
}

// Create singleton instance
const keyboardNav = new KeyboardNavManager();

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        keyboardNav.init();
    });
} else {
    keyboardNav.init();
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = KeyboardNavManager;
}
