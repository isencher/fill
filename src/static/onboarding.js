/**
 * Onboarding Module
 * Handles first-time user onboarding flow
 */

const ONBOARDING_STORAGE_KEY = 'fill_onboarding_completed';
const ONBOARDING_VERSION_KEY = 'fill_onboarding_version';
const CURRENT_ONBOARDING_VERSION = '1.0';

/**
 * Check if onboarding should be shown
 * @returns {boolean} True if onboarding should be shown
 */
function shouldShowOnboarding() {
    try {
        const completed = localStorage.getItem(ONBOARDING_STORAGE_KEY);
        const version = localStorage.getItem(ONBOARDING_VERSION_KEY);

        // Show onboarding if:
        // 1. Never completed before, OR
        // 2. Version has changed (new features to showcase)
        return !completed || version !== CURRENT_ONBOARDING_VERSION;
    } catch (error) {
        // If localStorage is not available, don't show onboarding
        console.error('Error accessing localStorage:', error);
        return false;
    }
}

/**
 * Mark onboarding as completed
 */
function markOnboardingCompleted() {
    try {
        localStorage.setItem(ONBOARDING_STORAGE_KEY, 'true');
        localStorage.setItem(ONBOARDING_VERSION_KEY, CURRENT_ONBOARDING_VERSION);
    } catch (error) {
        console.error('Error saving to localStorage:', error);
    }
}

/**
 * Reset onboarding (for testing purposes)
 */
function resetOnboarding() {
    try {
        localStorage.removeItem(ONBOARDING_STORAGE_KEY);
        localStorage.removeItem(ONBOARDING_VERSION_KEY);
    } catch (error) {
        console.error('Error resetting onboarding:', error);
    }
}

/**
 * Navigate to main application
 */
function navigateToApp() {
    window.location.href = '/static/index.html';
}

/**
 * Initialize onboarding page
 */
function initOnboarding() {
    const startBtn = document.getElementById('startBtn');
    const skipBtn = document.getElementById('skipBtn');

    if (startBtn) {
        startBtn.addEventListener('click', () => {
            markOnboardingCompleted();

            // Add a small delay for visual feedback
            startBtn.textContent = 'Getting Started...';
            startBtn.disabled = true;

            setTimeout(() => {
                navigateToApp();
            }, 300);
        });
    }

    if (skipBtn) {
        skipBtn.addEventListener('click', () => {
            markOnboardingCompleted();
            navigateToApp();
        });
    }

    // Add keyboard navigation
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
            markOnboardingCompleted();
            navigateToApp();
        }
    });
}

// Auto-redirect if onboarding was already completed
if (!shouldShowOnboarding()) {
    navigateToApp();
} else {
    // Initialize onboarding page
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initOnboarding);
    } else {
        initOnboarding();
    }
}

// Export functions for use in other modules
if (typeof window !== 'undefined') {
    window.Onboarding = {
        shouldShowOnboarding,
        markOnboardingCompleted,
        resetOnboarding,
        navigateToApp
    };
}
