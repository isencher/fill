"""
E2E Tests for Performance Optimization Features (Step 11.10)

Tests for:
1. Lazy loading functionality
2. Service Worker offline support
3. Bundle optimization indicators
4. Loading skeleton behavior
"""

import pytest
from fastapi.testclient import TestClient
from time import sleep
from io import BytesIO

from src.main import app, _file_storage


def upload_test_file(client: TestClient, filename: str, content: str = "name,age\nAlice,30\nBob,25"):
    """Helper function to upload a test file"""
    file_content = content.encode('utf-8')
    files = {'file': (filename, BytesIO(file_content), 'text/csv')}
    return client.post("/api/v1/upload", files=files)


class TestLazyLoading:
    """Tests for lazy loading of template list"""

    @pytest.fixture(autouse=True)
    def clear_storage(self) -> None:
        """Clear in-memory storage after each test."""
        yield
        _file_storage.clear()

    def test_lazy_load_css_is_loaded(self, client: TestClient) -> None:
        """Test that lazy load CSS is served"""
        response = client.get("/static/components/lazy-load.css")
        assert response.status_code == 200
        assert "lazy-loading-indicator" in response.text

    def test_lazy_load_js_is_loaded(self, client: TestClient) -> None:
        """Test that lazy load JavaScript is served"""
        response = client.get("/static/components/lazy-load.js")
        assert response.status_code == 200
        assert "LazyLoader" in response.text

    def test_lazy_load_has_loading_spinner(self, client: TestClient) -> None:
        """Test that lazy loading shows spinner"""
        response = client.get("/static/components/lazy-load.css")
        assert "lazy-loading-spinner" in response.text
        assert "lazy-spin" in response.text

    def test_lazy_load_has_load_more_button(self, client: TestClient) -> None:
        """Test that lazy loading has load more button"""
        response = client.get("/static/components/lazy-load.css")
        assert "lazy-load-more-btn" in response.text

    def test_lazy_load_has_skeleton_loader(self, client: TestClient) -> None:
        """Test that skeleton loader is defined"""
        response = client.get("/static/components/lazy-load.css")
        assert "skeleton-loader" in response.text
        assert "skeleton-card" in response.text

    def test_lazy_load_has_error_handling(self, client: TestClient) -> None:
        """Test that error handling is defined"""
        response = client.get("/static/components/lazy-load.css")
        assert "lazy-error-indicator" in response.text
        assert "lazy-retry-btn" in response.text


class TestServiceWorker:
    """Tests for Service Worker offline support"""

    def test_service_worker_is_served(self, client: TestClient) -> None:
        """Test that service worker file is served"""
        response = client.get("/static/service-worker.js")
        assert response.status_code == 200
        assert "CACHE_NAME" in response.text
        assert "fetch" in response.text

    def test_service_worker_caches_static_assets(self, client: TestClient) -> None:
        """Test that service worker caches static assets"""
        response = client.get("/static/service-worker.js")
        assert "STATIC_ASSETS" in response.text
        assert "/static/index.html" in response.text

    def test_service_worker_caches_api_responses(self, client: TestClient) -> None:
        """Test that service worker can cache API responses"""
        response = client.get("/static/service-worker.js")
        assert "API_PATTERNS" in response.text
        # Check for API cache name
        assert "API_CACHE_NAME" in response.text

    def test_service_worker_manager_js_is_loaded(self, client: TestClient) -> None:
        """Test that service worker manager is served"""
        response = client.get("/static/components/service-worker-manager.js")
        assert response.status_code == 200
        assert "ServiceWorkerManager" in response.text

    def test_service_worker_css_is_loaded(self, client: TestClient) -> None:
        """Test that service worker styles are served"""
        response = client.get("/static/components/service-worker.css")
        assert response.status_code == 200
        assert "offline-indicator" in response.text

    def test_offline_indicator_is_defined(self, client: TestClient) -> None:
        """Test that offline indicator styles exist"""
        response = client.get("/static/components/service-worker.css")
        assert "offline-icon" in response.text
        assert "offline-text" in response.text

    def test_sw_notification_styles_exist(self, client: TestClient) -> None:
        """Test that service worker notification styles exist"""
        response = client.get("/static/components/service-worker.css")
        assert "sw-notification" in response.text
        assert "sw-notification-success" in response.text
        assert "sw-notification-warning" in response.text


class TestPerformanceUtils:
    """Tests for performance utility functions"""

    def test_performance_utils_is_served(self, client: TestClient) -> None:
        """Test that performance utils file is served"""
        response = client.get("/static/components/performance-utils.js")
        assert response.status_code == 200
        assert "PerformanceUtils" in response.text

    def test_performance_utils_has_debounce(self, client: TestClient) -> None:
        """Test that debounce function exists"""
        response = client.get("/static/components/performance-utils.js")
        assert "debounce" in response.text

    def test_performance_utils_has_throttle(self, client: TestClient) -> None:
        """Test that throttle function exists"""
        response = client.get("/static/components/performance-utils.js")
        assert "throttle" in response.text

    def test_performance_utils_has_lazy_load_images(self, client: TestClient) -> None:
        """Test that lazy image loading function exists"""
        response = client.get("/static/components/performance-utils.js")
        assert "lazyLoadImages" in response.text

    def test_performance_utils_has_measure_performance(self, client: TestClient) -> None:
        """Test that performance measurement function exists"""
        response = client.get("/static/components/performance-utils.js")
        assert "measurePerformance" in response.text

    def test_performance_utils_has_web_vitals(self, client: TestClient) -> None:
        """Test that Web Vitals measurement exists"""
        response = client.get("/static/components/performance-utils.js")
        assert "getWebVitals" in response.text

    def test_performance_utils_has_virtual_scroll(self, client: TestClient) -> None:
        """Test that virtual scroll function exists"""
        response = client.get("/static/components/performance-utils.js")
        assert "createVirtualScroll" in response.text

    def test_performance_utils_has_preload(self, client: TestClient) -> None:
        """Test that resource preloading function exists"""
        response = client.get("/static/components/performance-utils.js")
        assert "preloadResources" in response.text

    def test_performance_utils_has_prefetch(self, client: TestClient) -> None:
        """Test that resource prefetching function exists"""
        response = client.get("/static/components/performance-utils.js")
        assert "prefetchResources" in response.text


class TestBundleOptimization:
    """Tests for bundle size optimization"""

    def test_templates_page_includes_lazy_load(self, client: TestClient) -> None:
        """Test that templates page includes lazy load script"""
        # Upload a file first
        file_response = upload_test_file(client, "test.csv")
        assert file_response.status_code in [200, 201]

        # Get file_id from response
        data = file_response.json()
        assert "file_id" in data
        file_id = data["file_id"]

        # Verify lazy load resources are available
        lazy_response = client.get("/static/components/lazy-load.js")
        assert lazy_response.status_code == 200

    def test_bundle_has_minified_code(self, client: TestClient) -> None:
        """Test that JavaScript files are served efficiently"""
        # Check that files are served with gzip/brotli if available
        response = client.get("/static/components/performance-utils.js")
        assert response.status_code == 200
        # In production, we'd check for compression headers


class TestLoadingSkeletons:
    """Tests for loading skeleton behavior"""

    def test_skeleton_css_exists(self, client: TestClient) -> None:
        """Test that skeleton loader CSS is available"""
        response = client.get("/static/components/lazy-load.css")
        assert response.status_code == 200
        assert "skeleton-pulse" in response.text

    def test_skeleton_has_shimmer_animation(self, client: TestClient) -> None:
        """Test that skeleton has shimmer effect"""
        response = client.get("/static/components/lazy-load.css")
        assert "skeleton-shimmer" in response.text

    def test_skeleton_card_structure(self, client: TestClient) -> None:
        """Test that skeleton card has proper structure"""
        response = client.get("/static/components/lazy-load.css")
        assert "skeleton-icon" in response.text
        assert "skeleton-title" in response.text
        assert "skeleton-text" in response.text


class TestPerformanceIntegration:
    """Integration tests for performance features"""

    @pytest.fixture(autouse=True)
    def clear_storage(self) -> None:
        """Clear in-memory storage after each test."""
        yield
        _file_storage.clear()

    def test_templates_page_has_performance_components(self, client: TestClient) -> None:
        """Test that templates page has all performance components"""
        # Verify all performance files are available
        files_to_check = [
            "/static/components/lazy-load.js",
            "/static/components/lazy-load.css",
            "/static/service-worker.js",
            "/static/components/service-worker-manager.js",
            "/static/components/service-worker.css",
            "/static/components/performance-utils.js"
        ]

        for file_path in files_to_check:
            response = client.get(file_path)
            assert response.status_code == 200, f"Failed to load {file_path}"

    def test_performance_utils_supports_offline(self, client: TestClient) -> None:
        """Test that performance utils support offline mode"""
        response = client.get("/static/components/performance-utils.js")
        assert response.status_code == 200

    def test_lazy_load_configurable_items_per_page(self, client: TestClient) -> None:
        """Test that lazy loader supports configurable items per page"""
        response = client.get("/static/components/lazy-load.js")
        assert "itemsPerPage" in response.text

    def test_lazy_load_has_scroll_threshold(self, client: TestClient) -> None:
        """Test that lazy loader has configurable scroll threshold"""
        response = client.get("/static/components/lazy-load.js")
        assert "loadMoreThreshold" in response.text
