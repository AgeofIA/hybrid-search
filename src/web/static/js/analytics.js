// Analytics-related functions
export function toggleAnalytics() {
    const content = document.getElementById('analyticsContent');
    const icon = document.getElementById('analyticsToggleIcon');
    
    content.classList.toggle('hidden');
    icon.setAttribute('data-feather', 
        content.classList.contains('hidden') ? 'chevron-down' : 'chevron-up'
    );
    feather.replace();
}

function formatNumber(num) {
    return new Intl.NumberFormat().format(num);
}

export function displaySearchAnalytics(analytics) {
    // Set query information
    document.getElementById('originalQuery').textContent = analytics.query;
    document.getElementById('normalizedQuery').textContent = analytics.normalized_query;
    
    // Set match statistics
    document.getElementById('totalCandidates').textContent = formatNumber(analytics.total_candidates);
    document.getElementById('qualifyingMatches').textContent = formatNumber(analytics.total_qualifying_matches);
    
    // Display groups found
    const groupsContainer = document.getElementById('groupsFound');
    const groupsFound = analytics.groups_found || [];
    groupsContainer.innerHTML = groupsFound.map(group => `
        <span class="px-2 py-1 text-sm font-medium bg-blue-100 text-blue-800 rounded-full">
            ${group}
        </span>
    `).join('');
    
    // Display matches per group
    const matchesContainer = document.getElementById('matchesPerGroup');
    const matchesPerGroup = analytics.matches_per_group || {};
    matchesContainer.innerHTML = Object.entries(matchesPerGroup).map(([group, count]) => `
        <div class="flex items-center justify-between">
            <span class="text-sm text-gray-700">${group}</span>
            <span class="text-sm font-medium text-gray-900">${count}</span>
        </div>
    `).join('');
    
    // Display current thresholds
    const thresholdsContainer = document.getElementById('currentThresholds');
    thresholdsContainer.innerHTML = `
        <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
            <p class="text-sm text-gray-600">Min Vector</p>
            <p class="text-lg font-medium text-gray-900 mt-1">
                ${analytics.thresholds.min_vector_score.toFixed(3)}
            </p>
        </div>
        <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
            <p class="text-sm text-gray-600">Min Keyword</p>
            <p class="text-lg font-medium text-gray-900 mt-1">
                ${analytics.thresholds.min_keyword_score.toFixed(3)}
            </p>
        </div>
        <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
            <p class="text-sm text-gray-600">Min Combined</p>
            <p class="text-lg font-medium text-gray-900 mt-1">
                ${analytics.thresholds.min_combined_score.toFixed(3)}
            </p>
        </div>
        <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
            <p class="text-sm text-gray-600">Reranking</p>
            <p class="text-lg font-medium ${analytics.reranking_enabled ? 'text-green-600' : 'text-gray-900'} mt-1">
                ${analytics.reranking_enabled ? 'Enabled' : 'Disabled'}
            </p>
        </div>
    `;
    
    // Update vector/keyword weight indicator and text
    const vectorWeight = parseFloat(document.getElementById('vectorWeight').value);
    const keywordWeight = (1 - vectorWeight).toFixed(2);
    
    // Update progress bar
    const indicator = document.getElementById('vectorWeightIndicator');
    indicator.style.width = `${vectorWeight * 100}%`;
    
    // Update weight split text
    document.getElementById('weightSplitText').textContent = 
        `Vector: ${(vectorWeight * 100).toFixed(0)}% / Keyword: ${(keywordWeight * 100).toFixed(0)}%`;
    
    // Show the analytics container (but keep content collapsed)
    document.getElementById('searchAnalytics').classList.remove('hidden');
}