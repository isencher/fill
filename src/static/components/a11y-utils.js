/**
 * Accessibility Utilities (A11y)
 * Helper functions for improving accessibility
 */

const A11yUtils = {
    /**
     * Announce message to screen readers
     */
    announce(message, priority = 'polite') {
        // Remove existing announcer
        const existing = document.getElementById('a11y-announcer');
        if (existing) {
            existing.remove();
        }

        // Create new announcer
        const announcer = document.createElement('div');
        announcer.id = 'a11y-announcer';
        announcer.setAttribute('role', 'status');
        announcer.setAttribute('aria-live', priority);
        announcer.setAttribute('aria-atomic', 'true');
        announcer.className = 'sr-only';

        announcer.textContent = message;

        document.body.appendChild(announcer);

        // Remove after announcement
        setTimeout(() => {
            announcer.remove();
        }, 1000);
    },

    /**
     * Create ARIA live region
     */
    createLiveRegion(id, priority = 'polite') {
        const region = document.createElement('div');
        region.id = id;
        region.setAttribute('role', 'status');
        region.setAttribute('aria-live', priority);
        region.setAttribute('aria-atomic', 'true');
        region.className = 'sr-only';

        return region;
    },

    /**
     * Set focus to element with scroll
     */
    setFocus(element, options = {}) {
        if (!element) return;

        const defaultOptions = {
            scroll: true,
            preventScroll: false
        };

        const mergedOptions = { ...defaultOptions, ...options };

        element.focus({
            preventScroll: mergedOptions.preventScroll
        });

        if (mergedOptions.scroll && !mergedOptions.preventScroll) {
            element.scrollIntoView({
                behavior: 'smooth',
                block: 'nearest'
            });
        }
    },

    /**
     * Trap focus within a container
     */
    trapFocus(container) {
        const focusableElements = container.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );

        const firstFocusable = focusableElements[0];
        const lastFocusable = focusableElements[focusableElements.length - 1];

        const handleKeyDown = (e) => {
            if (e.key !== 'Tab') return;

            if (e.shiftKey) {
                // Shift + Tab
                if (document.activeElement === firstFocusable) {
                    e.preventDefault();
                    lastFocusable.focus();
                }
            } else {
                // Tab
                if (document.activeElement === lastFocusable) {
                    e.preventDefault();
                    firstFocusable.focus();
                }
            }
        };

        container.addEventListener('keydown', handleKeyDown);

        // Return cleanup function
        return () => {
            container.removeEventListener('keydown', handleKeyDown);
        };
    },

    /**
     * Add ARIA attributes to element
     */
    setAria(element, attributes) {
        if (!element) return;

        Object.entries(attributes).forEach(([key, value]) => {
            if (key === 'label') {
                element.setAttribute('aria-label', value);
            } else if (key === 'labelledby') {
                element.setAttribute('aria-labelledby', value);
            } else if (key === 'describedby') {
                element.setAttribute('aria-describedby', value);
            } else if (key === 'live') {
                element.setAttribute('aria-live', value);
            } else if (key === 'expanded') {
                element.setAttribute('aria-expanded', value);
            } else if (key === 'hidden') {
                element.setAttribute('aria-hidden', value);
            } else if (key === 'selected') {
                element.setAttribute('aria-selected', value);
            } else if (key === 'checked') {
                element.setAttribute('aria-checked', value);
            } else if (key === 'disabled') {
                element.setAttribute('aria-disabled', value);
            } else if (key === 'pressed') {
                element.setAttribute('aria-pressed', value);
            } else if (key === 'haspopup') {
                element.setAttribute('aria-haspopup', value);
            } else if (key === 'controls') {
                element.setAttribute('aria-controls', value);
            } else if (key === 'current') {
                element.setAttribute('aria-current', value);
            } else if (key === 'role') {
                element.setAttribute('role', value);
            } else if (key === 'busy') {
                element.setAttribute('aria-busy', value);
            }
        });
    },

    /**
     * Remove ARIA attributes from element
     */
    removeAria(element, attributes) {
        if (!element) return;

        attributes.forEach(attr => {
            const ariaAttr = attr.startsWith('aria-') ? attr : `aria-${attr}`;
            element.removeAttribute(ariaAttr);
        });
    },

    /**
     * Check color contrast ratio
     */
    checkContrast(foreground, background) {
        // Convert hex to RGB
        const hexToRgb = (hex) => {
            const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
            return result ? {
                r: parseInt(result[1], 16),
                g: parseInt(result[2], 16),
                b: parseInt(result[3], 16)
            } : null;
        };

        const fg = hexToRgb(foreground);
        const bg = hexToRgb(background);

        if (!fg || !bg) return null;

        // Calculate relative luminance
        const getLuminance = (r, g, b) => {
            const [rs, gs, bs] = [r, g, b].map(val => {
                val = val / 255;
                return val <= 0.03928 ? val / 12.92 : Math.pow((val + 0.055) / 1.055, 2.4);
            });
            return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
        };

        const l1 = getLuminance(fg.r, fg.g, fg.b);
        const l2 = getLuminance(bg.r, bg.g, bg.b);

        const lighter = Math.max(l1, l2);
        const darker = Math.min(l1, l2);

        // Calculate contrast ratio
        return (lighter + 0.05) / (darker + 0.05);
    },

    /**
     * Verify WCAG AA compliance (4.5:1 for normal text, 3:1 for large text)
     */
    verifyWCAG_AA(foreground, background, isLargeText = false) {
        const ratio = this.checkContrast(foreground, background);
        if (!ratio) return null;

        const minimum = isLargeText ? 3.0 : 4.5;
        return {
            ratio: ratio.toFixed(2),
            passes: ratio >= minimum,
            level: ratio >= minimum ? 'AA' : 'Fail',
            minimum: minimum.toFixed(2)
        };
    },

    /**
     * Add keyboard event handler
     */
    addKeyboardHandler(element, handlers) {
        if (!element) return;

        element.addEventListener('keydown', (e) => {
            switch (e.key) {
                case 'Enter':
                case ' ':
                    if (handlers.activate && !e.repeat) {
                        e.preventDefault();
                        handlers.activate(e);
                    }
                    break;
                case 'Escape':
                    if (handlers.cancel) {
                        e.preventDefault();
                        handlers.cancel(e);
                    }
                    break;
                case 'ArrowUp':
                    if (handlers.previous) {
                        e.preventDefault();
                        handlers.previous(e);
                    }
                    break;
                case 'ArrowDown':
                    if (handlers.next) {
                        e.preventDefault();
                        handlers.next(e);
                    }
                    break;
                case 'ArrowLeft':
                    if (handlers.left) {
                        e.preventDefault();
                        handlers.left(e);
                    }
                    break;
                case 'ArrowRight':
                    if (handlers.right) {
                        e.preventDefault();
                        handlers.right(e);
                    }
                    break;
                case 'Home':
                    if (handlers.first) {
                        e.preventDefault();
                        handlers.first(e);
                    }
                    break;
                case 'End':
                    if (handlers.last) {
                        e.preventDefault();
                        handlers.last(e);
                    }
                    break;
            }
        });
    },

    /**
     * Make element focusable
     */
    makeFocusable(element, tabIndex = 0) {
        if (!element) return;

        if (!element.hasAttribute('tabindex')) {
            element.setAttribute('tabindex', tabIndex);
        }

        // Ensure keyboard interaction
        element.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                element.click();
            }
        });
    },

    /**
     * Add visual focus indicator
     */
    addFocusIndicator(element) {
        if (!element) return;

        element.classList.add('a11y-focus-visible');

        // Add focus-visible class only when navigating with keyboard
        element.addEventListener('keydown', () => {
            element.classList.add('a11y-focus-visible');
        });

        element.addEventListener('mousedown', () => {
            element.classList.remove('a11y-focus-visible');
        });
    },

    /**
     * Hide element from screen readers but keep visible
     */
    srOnly(element) {
        if (!element) return;

        element.classList.add('sr-only');

        // Add CSS if not present
        if (!document.getElementById('a11y-sr-only-style')) {
            const style = document.createElement('style');
            style.id = 'a11y-sr-only-style';
            style.textContent = `
                .sr-only {
                    position: absolute;
                    width: 1px;
                    height: 1px;
                    padding: 0;
                    margin: -1px;
                    overflow: hidden;
                    clip: rect(0, 0, 0, 0);
                    white-space: nowrap;
                    border-width: 0;
                }

                .sr-only:focus {
                    position: static;
                    width: auto;
                    height: auto;
                    padding: inherit;
                    margin: inherit;
                    overflow: visible;
                    clip: auto;
                    white-space: normal;
                }
            `;

            document.head.appendChild(style);
        }
    },

    /**
     * Add skip to main content link
     */
    addSkipLink(targetId = 'main-content') {
        const existing = document.getElementById('skip-link');
        if (existing) return;

        const skipLink = document.createElement('a');
        skipLink.id = 'skip-link';
        skipLink.href = `#${targetId}`;
        skipLink.textContent = 'Skip to main content';
        skipLink.className = 'skip-link';

        document.body.insertBefore(skipLink, document.body.firstChild);
    },

    /**
     * Initialize accessibility for the page
     */
    init() {
        // Add skip link
        this.addSkipLink();

        // Add live region for announcements
        const liveRegion = this.createLiveRegion('a11y-live-region');
        document.body.appendChild(liveRegion);

        // Add screen reader only styles
        this.srOnly(document.createElement('div'));

        // Add focus indicator styles
        if (!document.getElementById('a11y-focus-style')) {
            const style = document.createElement('style');
            style.id = 'a11y-focus-style';
            style.textContent = `
                .a11y-focus-visible:focus {
                    outline: 3px solid #667eea !important;
                    outline-offset: 2px !important;
                }

                .skip-link {
                    position: absolute;
                    top: -40px;
                    left: 0;
                    background: #667eea;
                    color: white;
                    padding: 8px 16px;
                    z-index: 10000;
                    text-decoration: none;
                    border-radius: 0 0 4px 0;
                    transition: top 0.2s ease;
                }

                .skip-link:focus {
                    top: 0;
                }

                /* Hide elements visually but keep accessible */
                [aria-hidden="true"] {
                    display: none !important;
                }

                /* Loading states */
                [aria-busy="true"] {
                    cursor: progress;
                }
            `;

            document.head.appendChild(style);
        }

        // Announce page ready
        this.announce('Page loaded and ready');
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = A11yUtils;
}
