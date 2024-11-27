// Configuration state variables
let FACTORY_DEFAULTS = null;  // True factory defaults
let SAVED_CONFIG = null;      // User-saved configuration
let ACTIVE_CONFIG = null;     // Currently active configuration

function showMessage(type, message) {
    const messageDiv = document.getElementById('configMessage');
    if (!messageDiv) return;

    messageDiv.textContent = message;
    messageDiv.className = `fixed bottom-4 right-4 flex items-center gap-2 px-4 py-2 rounded-md shadow-lg ${
        type === 'success' 
            ? 'bg-green-100 border border-green-200 text-green-700'
            : 'bg-amber-100 border border-amber-200 text-amber-700'
    }`;
    messageDiv.classList.remove('hidden');
    
    setTimeout(() => {
        messageDiv.classList.add('hidden');
    }, 2000);
}

// Initialize configuration from server
export async function initializeConfig() {
    try {
        // Load factory defaults first
        const defaultResponse = await fetch('/search/default-config');
        const defaultConfig = await defaultResponse.json();
        FACTORY_DEFAULTS = {
            vector_weight: defaultConfig.scoring_weights.vector_weight,
            keyword_weight: defaultConfig.scoring_weights.keyword_weight,
            min_vector_score: defaultConfig.thresholds.min_vector_score,
            min_keyword_score: defaultConfig.thresholds.min_keyword_score,
            min_combined_score: defaultConfig.thresholds.min_combined_score,
            enable_reranking: defaultConfig.reranking.enable_reranking
        };

        // Get current active configuration
        const activeResponse = await fetch('/search/config');
        ACTIVE_CONFIG = await activeResponse.json();

        // Try to load any saved configuration
        try {
            const savedResponse = await fetch('/search/saved-config');
            if (savedResponse.ok) {
                SAVED_CONFIG = await savedResponse.json();
                updateUIFromConfig(SAVED_CONFIG);
            } else {
                updateUIFromConfig(ACTIVE_CONFIG);
            }
        } catch (err) {
            updateUIFromConfig(ACTIVE_CONFIG);
        }
        
    } catch (err) {
        console.error('Failed to load search configuration:', err);
        const errorText = document.getElementById('errorText');
        const errorDiv = document.getElementById('error');
        errorText.textContent = 'Failed to load search configuration';
        errorDiv.classList.remove('hidden');
    }
}

// Helper to update all UI elements from a config object
function updateUIFromConfig(config) {
    // Update score weights
    document.getElementById('vectorWeight').value = config.vector_weight;
    document.getElementById('keywordWeight').value = config.keyword_weight;
    
    // Update thresholds
    document.getElementById('minVectorScore').value = config.min_vector_score;
    document.getElementById('minKeywordScore').value = config.min_keyword_score;
    document.getElementById('minCombinedScore').value = config.min_combined_score;
    
    // Update reranking configuration
    document.getElementById('enableReranking').checked = config.enable_reranking;
    
    // Update displayed values
    document.getElementById('vectorWeightValue').textContent = config.vector_weight;
    document.getElementById('keywordWeightValue').textContent = config.keyword_weight;
    
    // Validate all numeric inputs after setting values
    const numericInputs = [
        'vectorWeight', 'keywordWeight',
        'minVectorScore', 'minKeywordScore', 'minCombinedScore'
    ];
    
    numericInputs.forEach(id => {
        const input = document.getElementById(id);
        validateConfigInput(input);
    });
}

function validateConfigInput(input, isBlur = false) {
    const value = parseFloat(input.value);
    
    // During typing, allow empty, partial numbers, and decimals
    if (!isBlur && (input.value === '' || input.value === '.' || input.value === '0.')) {
        input.classList.remove('border-red-500', 'focus:ring-red-500', 'focus:border-red-500');
        input.classList.add('border-gray-300', 'focus:ring-blue-500', 'focus:border-blue-500');
        return true;
    }
    
    const isValid = !isNaN(value) && value >= 0 && value <= 1;
    
    if (!isValid) {
        input.classList.add('border-red-500', 'focus:ring-red-500', 'focus:border-red-500');
        input.classList.remove('border-gray-300', 'focus:ring-blue-500', 'focus:border-blue-500');
        
        // Only auto-correct values on blur
        if (isBlur) {
            if (isNaN(value) || value < 0) {
                input.value = 0;
            } else if (value > 1) {
                input.value = 1;
            }
            showMessage('error', 'Values must be between 0 and 1');
        }
    } else {
        input.classList.remove('border-red-500', 'focus:ring-red-500', 'focus:border-red-500');
        input.classList.add('border-gray-300', 'focus:ring-blue-500', 'focus:border-blue-500');
    }
    
    return isValid;
}

// Update event listeners to handle both input and blur events
document.addEventListener('DOMContentLoaded', () => {
    const numericInputs = [
        'minVectorScore', 'minKeywordScore', 'minCombinedScore'
    ];
    
    numericInputs.forEach(id => {
        const input = document.getElementById(id);
        input.addEventListener('input', () => validateConfigInput(input, false));
        input.addEventListener('blur', () => validateConfigInput(input, true));
    });
});

export async function resetToDefaults() {
    if (!FACTORY_DEFAULTS) {
        console.error('Cannot reset: factory defaults not loaded');
        showMessage('error', 'Unable to load default configuration');
        return;
    }

    try {
        const response = await fetch('/search/reset-config', {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error('Failed to reset configuration');
        }
        
        const result = await response.json();
        ACTIVE_CONFIG = result.config;
        updateUIFromConfig(FACTORY_DEFAULTS);
        showMessage('success', 'Reset to factory defaults');
        
    } catch (err) {
        console.error('Reset configuration error:', err);
        showMessage('error', 'Failed to reset configuration');
    }
}

export function loadSavedConfig() {
    if (!SAVED_CONFIG) {
        showMessage('error', 'No saved configuration available');
        return;
    }
    updateUIFromConfig(SAVED_CONFIG);
    showMessage('success', 'Saved configuration loaded');
}

export async function saveConfig() {
    const spinner = document.getElementById('saveSpinner');
    
    // Create a timeout to show spinner after 1 second
    const spinnerTimeout = setTimeout(() => {
        spinner.classList.remove('hidden');
    }, 1000);
    
    try {
        const response = await fetch('/search/saved-config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(getSearchConfig())
        });
        
        if (!response.ok) {
            throw new Error('Failed to save configuration');
        }
        
        // Update saved config reference
        SAVED_CONFIG = getSearchConfig();
        
        // Show success message
        showMessage('success', 'Configuration saved successfully');
        
    } catch (error) {
        console.error('Save configuration error:', error);
        showMessage('error', 'Failed to save configuration');
    } finally {
        // Clear the spinner timeout if it hasn't triggered yet
        clearTimeout(spinnerTimeout);
        // Hide the spinner if it was shown
        spinner.classList.add('hidden');
    }
}

export function toggleConfig() {
    const configPanel = document.getElementById('configPanel');
    const configIcon = document.getElementById('configIcon');
    
    configPanel.classList.toggle('hidden');
    configIcon.setAttribute('data-feather',
        configPanel.classList.contains('hidden') ? 'chevron-down' : 'chevron-up'
    );
    feather.replace();
}

export function updateWeights(vectorValue) {
    const keywordValue = (1 - vectorValue).toFixed(1);
    document.getElementById('vectorWeightValue').textContent = vectorValue;
    document.getElementById('keywordWeightValue').textContent = keywordValue;
    document.getElementById('keywordWeight').value = keywordValue;
}

export function getSearchConfig() {
    return {
        // Scoring weights
        vector_weight: parseFloat(document.getElementById('vectorWeight').value),
        keyword_weight: parseFloat(document.getElementById('keywordWeight').value),
        
        // Threshold settings
        min_vector_score: parseFloat(document.getElementById('minVectorScore').value),
        min_keyword_score: parseFloat(document.getElementById('minKeywordScore').value),
        min_combined_score: parseFloat(document.getElementById('minCombinedScore').value),
        
        // Reranking configuration
        enable_reranking: document.getElementById('enableReranking').checked
    };
}