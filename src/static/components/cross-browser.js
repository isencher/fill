/**
 * Cross-Browser Compatibility Utilities
 * Ensures consistent behavior across different browsers
 */

const BrowserCompat = {
    /**
     * Detect browser and version
     */
    getBrowserInfo() {
        const ua = navigator.userAgent;
        let browser = 'Unknown';
        let version = 'Unknown';

        if (ua.indexOf('Firefox') > -1) {
            browser = 'Firefox';
            version = ua.match(/Firefox\/(\d+)/)?.[1] || 'Unknown';
        } else if (ua.indexOf('Chrome') > -1 && ua.indexOf('Edg') === -1) {
            browser = 'Chrome';
            version = ua.match(/Chrome\/(\d+)/)?.[1] || 'Unknown';
        } else if (ua.indexOf('Safari') > -1 && ua.indexOf('Chrome') === -1) {
            browser = 'Safari';
            version = ua.match(/Version\/(\d+)/)?.[1] || 'Unknown';
        } else if (ua.indexOf('Edg') > -1) {
            browser = 'Edge';
            version = ua.match(/Edg\/(\d+)/)?.[1] || 'Unknown';
        } else if (ua.indexOf('MSIE') > -1 || ua.indexOf('Trident') > -1) {
            browser = 'IE';
            version = ua.match(/(?:MSIE |rv:)(\d+)/)?.[1] || 'Unknown';
        }

        return { browser, version, ua };
    },

    /**
     * Check if browser supports required features
     */
    checkFeatures() {
        const features = {
            localStorage: this._checkLocalStorage(),
            sessionStorage: this._checkSessionStorage(),
            fetch: typeof fetch !== 'undefined',
            promise: typeof Promise !== 'undefined',
            asyncAwait: (async () => {})() instanceof Promise,
            fileAPI: typeof File !== 'undefined' && typeof FileReader !== 'undefined',
            dragDrop: 'draggable' in document.createElement('div'),
            history: typeof history.pushState !== 'undefined',
            classList: 'classList' in document.createElement('div'),
            placeholder: 'placeholder' in document.createElement('input'),
            required: 'required' in document.createElement('input'),
            formData: typeof FormData !== 'undefined',
            blob: typeof Blob !== 'undefined',
            URL: typeof URL !== 'undefined',
            webWorker: typeof Worker !== 'undefined',
            serviceWorker: 'serviceWorker' in navigator,
            intersectionObserver: typeof IntersectionObserver !== 'undefined',
            requestIdleCallback: typeof requestIdleCallback !== 'undefined'
        };

        const supported = Object.values(features).every(f => f === true);
        const missing = Object.entries(features)
            .filter(([_, supported]) => !supported)
            .map(([feature]) => feature);

        return {
            supported,
            features,
            missing,
            isLegacy: !features.promise || !features.fetch
        };
    },

    _checkLocalStorage() {
        try {
            const test = '__localStorage_test__';
            localStorage.setItem(test, test);
            localStorage.removeItem(test);
            return true;
        } catch (e) {
            return false;
        }
    },

    _checkSessionStorage() {
        try {
            const test = '__sessionStorage_test__';
            sessionStorage.setItem(test, test);
            sessionStorage.removeItem(test);
            return true;
        } catch (e) {
            return false;
        }
    },

    /**
     * Check if browser is supported
     */
    isSupported(minVersions = {
        Chrome: 90,
        Firefox: 88,
        Safari: 14,
        Edge: 90,
        IE: null // IE not supported
    }) {
        const info = this.getBrowserInfo();
        const minVersion = minVersions[info.browser];

        if (minVersion === null) {
            return false; // Browser explicitly not supported
        }

        if (minVersion === undefined) {
            return true; // Unknown browser, assume support
        }

        return parseInt(info.version) >= minVersion;
    },

    /**
     * Apply polyfills if needed
     */
    applyPolyfills() {
        // Polyfill for.closest() if needed
        if (!Element.prototype.matches) {
            Element.prototype.matches = Element.prototype.msMatchesSelector ||
                Element.prototype.webkitMatchesSelector;
        }

        if (!Element.prototype.closest) {
            Element.prototype.closest = function(s) {
                let el = this;
                do {
                    if (el.matches(s)) return el;
                    el = el.parentElement || el.parentNode;
                } while (el !== null && el.nodeType === 1);
                return null;
            };
        }

        // Polyfill for Array.from()
        if (!Array.from) {
            Array.from = (function() {
                const toStr = Object.prototype.toString;
                const isCallable = function(fn) {
                    return typeof fn === 'function' || toStr.call(fn) === '[object Function]';
                };
                const toInteger = function(value) {
                    const number = Number(value);
                    if (isNaN(number)) { return 0; }
                    if (number === 0 || !isFinite(number)) { return number; }
                    return (number > 0 ? 1 : -1) * Math.floor(Math.abs(number));
                };
                const maxSafeInteger = Math.pow(2, 53) - 1;
                return function from(arrayLike/*, mapFn, thisArg */) {
                    const C = this;
                    const items = Object(arrayLike);

                    if (arrayLike == null) {
                        throw new TypeError('Array.from requires an array-like object - not null or undefined');
                    }

                    const mapFn = arguments.length > 1 ? arguments[1] : void undefined;
                    let T;
                    if (typeof mapFn !== 'undefined') {
                        if (!isCallable(mapFn)) {
                            throw new TypeError('Array.from: when provided, the second argument must be a function');
                        }
                        if (arguments.length > 2) {
                            T = arguments[2];
                        }
                    }

                    const len = toInteger(items.length);
                    const A = isCallable(C) ? Object(new C(len)) : new Array(len);
                    let k = 0;
                    let kValue;

                    while (k < len) {
                        kValue = items[k];
                        if (mapFn) {
                            A[k] = typeof T === 'undefined' ? mapFn(kValue, k) : mapFn.call(T, kValue, k);
                        } else {
                            A[k] = kValue;
                        }
                        k += 1;
                    }
                    A.length = len;
                    return A;
                };
            }());
        }

        // Polyfill for Object.assign()
        if (typeof Object.assign !== 'function') {
            Object.assign = function(target, varArgs) {
                if (target == null) {
                    throw new TypeError('Cannot convert undefined or null to object');
                }
                const to = Object(target);
                for (let index = 1; index < arguments.length; index++) {
                    const nextSource = arguments[index];
                    if (nextSource != null) {
                        for (const nextKey in nextSource) {
                            if (Object.prototype.hasOwnProperty.call(nextSource, nextKey)) {
                                to[nextKey] = nextSource[nextKey];
                            }
                        }
                    }
                }
                return to;
            };
        }

        console.log('[BrowserCompat] Polyfills applied');
    },

    /**
     * Show unsupported browser message
     */
    showUnsupportedMessage(container = document.body) {
        const info = this.getBrowserInfo();
        const features = this.checkFeatures();

        const message = document.createElement('div');
        message.className = 'browser-unsupported-banner';
        message.innerHTML = `
            <div class="browser-unsupported-content">
                <div class="browser-unsupported-icon">⚠️</div>
                <h3>Unsupported Browser</h3>
                <p>Your browser (${info.browser} ${info.version}) is not supported.</p>
                <p>Please use one of the following browsers:</p>
                <ul>
                    <li>Chrome 90+</li>
                    <li>Firefox 88+</li>
                    <li>Safari 14+</li>
                    <li>Edge 90+</li>
                </ul>
                ${features.missing.length > 0 ? `
                    <p class="missing-features">Missing features: ${features.missing.join(', ')}</p>
                ` : ''}
            </div>
        `;

        container.insertBefore(message, container.firstChild);
    },

    /**
     * Run compatibility check on page load
     */
    init() {
        console.log('[BrowserCompat] Checking compatibility...');

        const info = this.getBrowserInfo();
        console.log(`[BrowserCompat] Browser: ${info.browser} ${info.version}`);

        const features = this.checkFeatures();
        console.log('[BrowserCompat] Features:', features);

        if (!features.supported) {
            console.warn('[BrowserCompat] Missing features:', features.missing);
        }

        const supported = this.isSupported();
        console.log(`[BrowserCompat] Supported: ${supported}`);

        // Apply polyfills
        this.applyPolyfills();

        // Show message if unsupported
        if (!supported) {
            this.showUnsupportedMessage();
        }

        return {
            info,
            features,
            supported
        };
    },

    /**
     * Add browser-specific CSS classes
     */
    addBrowserClasses() {
        const info = this.getBrowserInfo();
        document.documentElement.classList.add(`browser-${info.browser.toLowerCase()}`);
        document.documentElement.classList.add(`browser-${info.browser.toLowerCase()}-${info.version}`);

        if (info.browser === 'IE' || parseInt(info.version) < 90) {
            document.documentElement.classList.add('legacy-browser');
        }
    },

    /**
     * Test specific API compatibility
     */
    testAPI(apiName, testFunction) {
        try {
            const result = testFunction();
            console.log(`[BrowserCompat] ${apiName}: ✓ Supported`);
            return { supported: true, result };
        } catch (error) {
            console.warn(`[BrowserCompat] ${apiName}: ✗ Not supported`, error);
            return { supported: false, error: error.message };
        }
    }
};

// Auto-initialize on load
if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            BrowserCompat.init();
            BrowserCompat.addBrowserClasses();
        });
    } else {
        BrowserCompat.init();
        BrowserCompat.addBrowserClasses();
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = BrowserCompat;
}
