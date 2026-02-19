/**
 * Performance Utilities
 * Helper functions for performance optimization
 */

const PerformanceUtils = {
    /**
     * Debounce function execution
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    /**
     * Throttle function execution
     */
    throttle(func, limit) {
        let inThrottle;
        return function executedFunction(...args) {
            if (!inThrottle) {
                func(...args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    /**
     * Request animation frame throttle
     */
    rafThrottle(func) {
        let rafId = null;
        return function executedFunction(...args) {
            if (rafId === null) {
                rafId = requestAnimationFrame(() => {
                    func(...args);
                    rafId = null;
                });
            }
        };
    },

    /**
     * Lazy load images
     */
    lazyLoadImages() {
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        const src = img.dataset.src;

                        if (src) {
                            img.src = src;
                            img.removeAttribute('data-src');
                            observer.unobserve(img);
                        }
                    }
                });
            });

            const images = document.querySelectorAll('img[data-src]');
            images.forEach(img => imageObserver.observe(img));
        }
    },

    /**
     * Measure and log performance metrics
     */
    measurePerformance(label) {
        if (window.performance && performance.mark) {
            performance.mark(`${label}-start`);
        }

        return () => {
            if (window.performance && performance.mark && performance.measure) {
                performance.mark(`${label}-end`);
                performance.measure(label, `${label}-start`, `${label}-end`);

                const entries = performance.getEntriesByName(label);
                const lastEntry = entries[entries.length - 1];

                console.log(`[Performance] ${label}:`, Math.round(lastEntry.duration), 'ms');

                // Clean up
                performance.clearMarks(`${label}-start`);
                performance.clearMarks(`${label}-end`);
                performance.clearMeasures(label);
            }
        };
    },

    /**
     * Get Web Vitals metrics
     */
    getWebVitals() {
        return new Promise((resolve) => {
            if (!('PerformanceObserver' in window)) {
                resolve(null);
                return;
            }

            const vitals = {};

            // Largest Contentful Paint (LCP)
            try {
                const lcpObserver = new PerformanceObserver((list) => {
                    const entries = list.getEntries();
                    const lastEntry = entries[entries.length - 1];
                    vitals.lcp = lastEntry.renderTime || lastEntry.loadTime;
                });
                lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
            } catch (e) {
                console.warn('LCP not supported');
            }

            // First Input Delay (FID)
            try {
                const fidObserver = new PerformanceObserver((list) => {
                    const entries = list.getEntries();
                    vitals.fid = entries[0].processingStart - entries[0].startTime;
                });
                fidObserver.observe({ entryTypes: ['first-input'] });
            } catch (e) {
                console.warn('FID not supported');
            }

            // Cumulative Layout Shift (CLS)
            try {
                let clsScore = 0;
                const clsObserver = new PerformanceObserver((list) => {
                    list.getEntries().forEach(entry => {
                        if (!entry.hadRecentInput) {
                            clsScore += entry.value;
                        }
                    });
                    vitals.cls = clsScore;
                });
                clsObserver.observe({ entryTypes: ['layout-shift'] });
            } catch (e) {
                console.warn('CLS not supported');
            }

            // Time to First Byte (TTFB)
            try {
                const ttfb = performance.getEntriesByType('navigation')[0]?.responseStart;
                if (ttfb) {
                    vitals.ttfb = ttfb;
                }
            } catch (e) {
                console.warn('TTFB not available');
            }

            // Resolve after a short delay to allow metrics to be collected
            setTimeout(() => resolve(vitals), 3000);
        });
    },

    /**
     * Report performance metrics to analytics
     */
    reportMetrics(metrics) {
        // Send to analytics service
        if (window.gtag) {
            gtag('event', 'timing_complete', {
                name: 'page_load',
                value: metrics.pageLoad || 0,
                event_category: 'performance'
            });
        }

        // Log to console for debugging
        console.table(metrics);
    },

    /**
     * Optimize images for current device pixel ratio
     */
    getOptimalImageUrl(baseUrl, width, height) {
        const dpr = window.devicePixelRatio || 1;
        const optimizedWidth = width * dpr;
        const optimizedHeight = height * dpr;

        // Append size parameters to URL
        const url = new URL(baseUrl, window.location.origin);
        url.searchParams.set('w', optimizedWidth);
        url.searchParams.set('h', optimizedHeight);
        url.searchParams.set('dpr', dpr);

        return url.toString();
    },

    /**
     * Preload critical resources
     */
    preloadResources(resources) {
        resources.forEach(resource => {
            const link = document.createElement('link');
            link.rel = 'preload';

            if (resource.as) {
                link.as = resource.as;
            }

            if (resource.type) {
                link.type = resource.type;
            }

            if (resource.crossorigin) {
                link.crossOrigin = resource.crossorigin;
            }

            link.href = resource.url;
            document.head.appendChild(link);
        });
    },

    /**
     * Prefetch resources for next page navigation
     */
    prefetchResources(resources) {
        resources.forEach(resource => {
            const link = document.createElement('link');
            link.rel = 'prefetch';
            link.href = resource;
            document.head.appendChild(link);
        });
    },

    /**
     * Reduce JavaScript execution time with code splitting
     */
    async loadModule(modulePath) {
        try {
            const module = await import(modulePath);
            return module;
        } catch (error) {
            console.error('Failed to load module:', modulePath, error);
            return null;
        }
    },

    /**
     * Virtual scroll implementation for large lists
     */
    createVirtualScroll(options) {
        const {
            container,
            itemHeight,
            renderItem,
            getTotalItems,
            getItemData
        } = options;

        let visibleStart = 0;
        let visibleEnd = 0;
        const bufferSize = 5;

        function updateVisibleRange() {
            const scrollTop = container.scrollTop;
            const containerHeight = container.offsetHeight;

            visibleStart = Math.max(0, Math.floor(scrollTop / itemHeight) - bufferSize);
            visibleEnd = Math.min(
                getTotalItems(),
                Math.ceil((scrollTop + containerHeight) / itemHeight) + bufferSize
            );
        }

        function render() {
            updateVisibleRange();

            const totalHeight = getTotalItems() * itemHeight;
            const offsetY = visibleStart * itemHeight;

            // Update container styles
            container.style.height = `${totalHeight}px`;
            container.style.position = 'relative';
            container.style.overflow = 'auto';

            // Clear existing items
            const existingItems = container.querySelectorAll('[data-virtual-item]');
            existingItems.forEach(item => item.remove());

            // Render visible items
            const fragment = document.createDocumentFragment();

            for (let i = visibleStart; i < visibleEnd; i++) {
                const itemData = getItemData(i);
                const itemElement = renderItem(itemData, i);

                itemElement.setAttribute('data-virtual-item', 'true');
                itemElement.style.position = 'absolute';
                itemElement.style.top = `${i * itemHeight}px`;
                itemElement.style.height = `${itemHeight}px`;

                fragment.appendChild(itemElement);
            }

            container.appendChild(fragment);
        }

        // Throttled scroll handler
        const handleScroll = PerformanceUtils.throttle(() => {
            window.requestAnimationFrame(render);
        }, 16);

        container.addEventListener('scroll', handleScroll);

        // Initial render
        render();

        return {
            update: render,
            destroy: () => {
                container.removeEventListener('scroll', handleScroll);
            }
        };
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PerformanceUtils;
}
