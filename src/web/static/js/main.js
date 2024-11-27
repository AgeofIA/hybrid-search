import { 
    toggleConfig, 
    updateWeights, 
    getSearchConfig, 
    initializeConfig, 
    resetToDefaults,
    saveConfig, 
    loadSavedConfig 
} from './config.js';
import { toggleAnalytics, displaySearchAnalytics } from './analytics.js';
import { 
    displayResults, 
    displayExactMatch,
    toggleDetails 
} from './results/subtitles.js';

// Initialize Feather icons
feather.replace();

// DOM Elements
const elements = {
    searchInput: document.getElementById('searchInput'),
    searchButton: document.getElementById('searchButton'),
    loadingDiv: document.getElementById('loading'),
    errorDiv: document.getElementById('error'),
    errorText: document.getElementById('errorText'),
    resultsDiv: document.getElementById('results'),
    noResultsDiv: document.getElementById('noResults'),
    clearSearchBtn: document.getElementById('clearSearch'),
    searchAnalytics: document.getElementById('searchAnalytics'),
    exactMatchDiv: document.getElementById('exactMatch')
};

// Export functions for global access
window.toggleConfig = toggleConfig;
window.updateWeights = updateWeights;
window.resetToDefaults = resetToDefaults;
window.saveConfig = saveConfig;
window.loadSavedConfig = loadSavedConfig;
window.toggleAnalytics = toggleAnalytics;
window.toggleDetails = toggleDetails;

/**
 * Reset the search interface to its initial state
 */
function resetSearchUI() {
    elements.searchInput.value = '';
    elements.clearSearchBtn.classList.add('hidden');
    elements.exactMatchDiv.classList.add('hidden');
    elements.resultsDiv.innerHTML = '';
    elements.searchAnalytics.classList.add('hidden');
    elements.noResultsDiv.classList.add('hidden');
    elements.searchInput.focus();
}

/**
 * Show an error message to the user
 * @param {string} message - The error message to display
 */
function showError(message) {
    elements.errorText.textContent = message;
    elements.errorDiv.classList.remove('hidden');
}

/**
 * Reset UI elements before a new search
 */
function prepareForSearch() {
    elements.loadingDiv.classList.remove('hidden');
    elements.errorDiv.classList.add('hidden');
    elements.noResultsDiv.classList.add('hidden');
    elements.searchAnalytics.classList.add('hidden');
    elements.exactMatchDiv.classList.add('hidden');
    elements.searchButton.disabled = true;
    elements.resultsDiv.innerHTML = '';
}

/**
 * Perform the search operation
 * @returns {Promise<void>}
 */
async function performSearch() {
    const query = elements.searchInput.value.trim();
    if (!query) {
        showError('Please enter a search query');
        return;
    }

    prepareForSearch();

    try {
        const response = await fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query,
                config: getSearchConfig()
            })
        });

        // Check for non-JSON responses (like HTML error pages)
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            throw new Error('Server returned an invalid response. Please try again.');
        }

        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || `Search failed: ${response.statusText}`);
        }

        // Process search results
        if (data.search_metadata) {
            displaySearchAnalytics(data.search_metadata);
        }

        if (data.exact_match) {
            await displayExactMatch(data.exact_match);
        }

        if (!data.matches || data.matches.length === 0) {
            elements.noResultsDiv.classList.remove('hidden');
            return;
        }

        await displayResults(data.matches);

    } catch (error) {
        console.error('Search error:', error);
        showError(error.message || 'An unexpected error occurred during search');
    } finally {
        elements.loadingDiv.classList.add('hidden');
        elements.searchButton.disabled = false;
    }
}

// Event Listeners
function initializeEventListeners() {
    // Clear search functionality
    elements.clearSearchBtn.addEventListener('click', resetSearchUI);

    // Show/hide clear button based on input
    elements.searchInput.addEventListener('input', () => {
        elements.clearSearchBtn.classList.toggle('hidden', !elements.searchInput.value);
    });

    // Search button click
    elements.searchButton.addEventListener('click', (e) => {
        e.preventDefault();
        performSearch();
    });

    // Enter key handler
    elements.searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            performSearch();
        }
    });
}

// Initialize the application
async function initialize() {
    await initializeConfig();
    initializeEventListeners();
}

// Start the application
initialize().catch(error => {
    console.error('Failed to initialize application:', error);
    showError('Failed to initialize application. Please refresh the page.');
});