/**
 * Service Worker for Offline Support
 * Caches static assets and API responses
 */

const CACHE_NAME = 'fill-v1.0.0';
const API_CACHE_NAME = 'fill-api-v1.0.0';

// Static assets to cache immediately
const STATIC_ASSETS = [
    '/',
    '/static/index.html',
    '/static/templates.html',
    '/static/mapping.html',
    '/static/onboarding.html',
    '/static/components/progress.css',
    '/static/components/empty-state.css',
    '/static/components/animations.css',
    '/static/components/help-tooltip.css',
    '/static/components/faq-modal.css',
    '/static/components/tour.css',
    '/static/components/lazy-load.css',
    '/static/mobile.css',
    '/static/components/progress.js',
    '/static/components/empty-state.js',
    '/static/components/skeleton.js',
    '/static/components/lazy-load.js',
    '/static/components/help-tooltip.js',
    '/static/components/faq-modal.js',
    '/static/components/tour.js',
    '/static/upload.js',
    '/static/templates.js',
    '/static/mapping.js',
    '/static/onboarding.js',
    '/static/samples/sample-customer-data.csv'
];

// API endpoints to cache
const API_PATTERNS = [
    /\/api\/v1\/templates/,
    /\/api\/v1\/files/,
    /\/api\/v1\/parse\//
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
    console.log('[Service Worker] Installing...');

    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            console.log('[Service Worker] Caching static assets');
            return cache.addAll(STATIC_ASSETS);
        }).then(() => {
            // Force the waiting service worker to become the active service worker
            return self.skipWaiting();
        })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    console.log('[Service Worker] Activating...');

    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    // Delete old caches
                    if (cacheName !== CACHE_NAME && cacheName !== API_CACHE_NAME) {
                        console.log('[Service Worker] Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => {
            // Take control of all pages immediately
            return self.clients.claim();
        })
    );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }

    // Skip cross-origin requests
    if (url.origin !== location.origin) {
        return;
    }

    // Handle API requests
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(handleApiRequest(request));
        return;
    }

    // Handle static asset requests
    event.respondWith(handleStaticRequest(request));
});

/**
 * Handle API requests with network-first strategy
 */
async function handleApiRequest(request) {
    const url = new URL(request.url);

    // Check if this API should be cached
    const shouldCache = API_PATTERNS.some(pattern => pattern.test(url.pathname));

    if (!shouldCache) {
        // Don't cache, just fetch from network
        return fetch(request);
    }

    // Network-first strategy for API calls
    try {
        // Try network first
        const networkResponse = await fetch(request);

        if (networkResponse.ok) {
            // Cache successful responses
            const cache = await caches.open(API_CACHE_NAME);
            cache.put(request, networkResponse.clone());
        }

        return networkResponse;
    } catch (error) {
        console.log('[Service Worker] Network failed, trying cache:', request.url);

        // Fallback to cache
        const cache = await caches.open(API_CACHE_NAME);
        const cachedResponse = await cache.match(request);

        if (cachedResponse) {
            console.log('[Service Worker] Serving from cache:', request.url);
            return cachedResponse;
        }

        // Return offline fallback
        return new Response(
            JSON.stringify({ error: 'Offline - no cached data available' }),
            {
                status: 503,
                headers: { 'Content-Type': 'application/json' }
            }
        );
    }
}

/**
 * Handle static asset requests with cache-first strategy
 */
async function handleStaticRequest(request) {
    // Cache-first strategy for static assets
    const cache = await caches.open(CACHE_NAME);
    const cachedResponse = await cache.match(request);

    if (cachedResponse) {
        console.log('[Service Worker] Serving from cache:', request.url);
        return cachedResponse;
    }

    try {
        // Fetch from network
        const networkResponse = await fetch(request);

        if (networkResponse.ok) {
            // Cache the response
            cache.put(request, networkResponse.clone());
        }

        return networkResponse;
    } catch (error) {
        console.log('[Service Worker] Fetch failed:', request.url);

        // Return offline page for HTML requests
        if (request.headers.get('accept').includes('text/html')) {
            return caches.match('/static/onboarding.html') || new Response('Offline', {
                status: 503,
                headers: { 'Content-Type': 'text/html' }
            });
        }

        // For other requests, just fail
        throw error;
    }
}

// Message event - handle messages from clients
self.addEventListener('message', (event) => {
    const { data } = event;

    if (data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }

    if (data.type === 'CLEAR_CACHE') {
        event.waitUntil(
            caches.keys().then((cacheNames) => {
                return Promise.all(
                    cacheNames.map((cacheName) => caches.delete(cacheName))
                );
            })
        );
    }

    if (data.type === 'GET_CACHE_SIZE') {
        event.waitUntil(
            Promise.all([
                caches.open(CACHE_NAME).then(cache => cache.keys()),
                caches.open(API_CACHE_NAME).then(cache => cache.keys())
            ]).then(([staticKeys, apiKeys]) => {
                event.ports[0].postMessage({
                    type: 'CACHE_SIZE',
                    staticCount: staticKeys.length,
                    apiCount: apiKeys.length,
                    total: staticKeys.length + apiKeys.length
                });
            })
        );
    }
});
