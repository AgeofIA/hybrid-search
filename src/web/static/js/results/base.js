// Core result generation and display functionality

/**
 * Generate base container for a result
 * @param {Object} options Container configuration
 * @param {string} options.content Inner content HTML
 * @param {Object} options.colors Theme colors for the container
 * @param {string} options.displayIndex Unique identifier for this result
 * @param {boolean} options.isExpandable Whether the result can be expanded
 * @returns {string} Container HTML
 */
export function generateBaseResult(options) {
    const {
        content,
        colors = {
            bg: 'bg-white',
            border: 'border-gray-200'
        },
        displayIndex = 'result',
        isExpandable = true
    } = options;

    return `
        <div class="${colors.bg} rounded-lg shadow-sm border ${colors.border} overflow-hidden hover:shadow-md transition-shadow duration-200 ${isExpandable ? 'cursor-pointer' : ''}"
             ${isExpandable ? `onclick="toggleDetails('${displayIndex}')"` : ''}>
            <div class="p-6">
                ${content}
            </div>
        </div>
    `;
}

/**
 * Generate score pills section
 * @param {Object} scores Score values
 * @param {Object} colors Theme colors for pills
 * @returns {string} Score pills HTML
 */
export function generateScorePills(scores, colors) {
    const defaultColors = {
        combined: 'bg-rose-50 text-rose-700',
        vector: 'bg-sky-50 text-sky-700',
        keyword: 'bg-violet-50 text-violet-700'
    };

    const pillColors = { ...defaultColors, ...colors };

    return `
        <div class="flex flex-wrap gap-2">
            <span class="text-xs font-mono ${pillColors.combined} px-2 py-1 rounded-full flex items-center gap-1"
                  title="Combined Score">
                <svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
                </svg>
                ${scores.combined.toFixed(3)}
            </span>
            <span class="text-xs font-mono ${pillColors.vector} px-2 py-1 rounded-full flex items-center gap-1"
                  title="Vector Score">
                <svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
                </svg>
                ${scores.vector.toFixed(3)}
            </span>
            <span class="text-xs font-mono ${pillColors.keyword} px-2 py-1 rounded-full flex items-center gap-1"
                  title="Keyword Score">
                <svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M17 3a2.85 2.85 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"/>
                </svg>
                ${scores.keyword.toFixed(3)}
            </span>
        </div>
    `;
}

/**
 * Generate ranking pills
 * @param {Object} options Ranking configuration
 * @returns {string} Ranking pills HTML
 */
export function generateRankingPills(options) {
    const {
        combinedScoreRank,
        isReranking,
        rerankedPosition,
        isExactMatch
    } = options;

    const basePillClass = "text-xs font-mono px-2 py-1 rounded-full flex items-center gap-1";
    const matchPillClass = `${basePillClass} bg-rose-50 text-rose-700`;
    const rerankPillClass = `${basePillClass} bg-emerald-50 text-emerald-700`;
    
    let pills = '';
    
    if (isReranking) {
        pills += `
            <span class="${rerankPillClass}" title="Reranked Position">
                <svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/>
                </svg>
                ${rerankedPosition}
            </span>
        `;
    }

    if (!isExactMatch) {
        pills += `
            <span class="${matchPillClass}" title="Match Order by Combined Score">
                <svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M3 6h18M3 12h18M3 18h18"/>
                </svg>
                ${combinedScoreRank}
            </span>
        `;
    }

    return pills;
}

/**
 * Toggle expandable details sections
 * @param {string} index Result identifier
 */
export function toggleDetails(index) {
    const metadataDiv = document.querySelector(`.metadata-${index}`);
    const toggleIcon = document.querySelector(`.toggle-icon-${index}`);
    
    if (!metadataDiv || !toggleIcon) return;
    
    metadataDiv.classList.toggle('hidden');

    if (metadataDiv.classList.contains('hidden')) {
        toggleIcon.setAttribute('data-feather', 'chevron-down');
    } else {
        toggleIcon.setAttribute('data-feather', 'chevron-up');
    }
    
    feather.replace();
}

/**
 * Generate toggle button
 * @param {string} displayIndex Result identifier
 * @returns {string} Toggle button HTML
 */
export function generateToggleButton(displayIndex) {
    return `
        <button
            onclick="toggleDetails('${displayIndex}'); event.stopPropagation();"
            class="text-gray-500 hover:text-gray-700 focus:outline-none p-2 rounded-full hover:bg-gray-100"
            aria-label="Toggle details"
        >
            <i data-feather="chevron-down" class="toggle-icon-${displayIndex} w-5 h-5"></i>
        </button>
    `;
}