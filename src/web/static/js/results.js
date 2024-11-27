// Load schema configuration
let SCHEMA_CONFIG = null;

async function loadSchemaConfig() {
    try {
        const response = await fetch(`/metadata/schema/frontend-config`);
        if (!response.ok) {
            throw new Error(`Failed to load schema: ${response.statusText}`);
        }
        SCHEMA_CONFIG = await response.json();
        return SCHEMA_CONFIG;
    } catch (error) {
        console.error('Failed to load schema configuration:', error);
        // Provide fallback default configuration
        SCHEMA_CONFIG = {
            path_fields: [],
            primary_detail: null,
            secondary_details: [],
            main_content_field: 'text'
        };
        return SCHEMA_CONFIG;
    }
}

// Initialize schema configuration when the page loads
document.addEventListener('DOMContentLoaded', async () => {
    await loadSchemaConfig();
});

// Generate HTML for a single result (used for both exact and regular matches)
async function generateResultHTML(match, isExactMatch = false, displayIndex = 'exact') {
    // Ensure schema config is loaded
    if (!SCHEMA_CONFIG) {
        await loadSchemaConfig();
    }
    
    return isExactMatch ? 
        generateExactMatchHTML(match) : 
        generateStandardResultHTML(match, displayIndex);
}

// Generate HTML for an exact match
function generateExactMatchHTML(match) {
    const baseColors = {
        bg: 'bg-blue-50',
        border: 'border-blue-200',
        pill: 'bg-blue-100 text-blue-700'
    };

    return `
        <div class="${baseColors.bg} rounded-lg shadow-sm border ${baseColors.border} overflow-hidden hover:shadow-md transition-shadow duration-200 cursor-pointer"
             onclick="toggleDetails('exact')">
            <div class="p-6">
                <!-- Exact Match Badge -->
                <div class="flex items-center justify-between gap-2 mb-4">
                    <div class="flex items-center gap-2">
                        <i data-feather="check-circle" class="w-5 h-5 text-blue-600"></i>
                        <span class="text-lg font-semibold text-blue-900">Exact Match Found</span>
                    </div>
                    <div class="flex items-center gap-4">
                        ${generateScorePillsSection(match, baseColors.pill)}
                        <button
                            onclick="toggleDetails('exact'); event.stopPropagation();"
                            class="text-gray-500 hover:text-gray-700 focus:outline-none p-2 rounded-full hover:bg-gray-100"
                            aria-label="Toggle details"
                        >
                            <i data-feather="chevron-down" class="toggle-icon-exact w-5 h-5"></i>
                        </button>
                    </div>
                </div>
                ${generateResultContent(match, true, 'exact', baseColors, false, false)}
            </div>
        </div>
    `;
}

// Generate HTML for a standard result
function generateStandardResultHTML(match, displayIndex) {
    const baseColors = {
        bg: 'bg-white',
        border: 'border-gray-200',
        pill: {
            rank: 'bg-rose-50 text-rose-700',     // For match number and combined score
            vector: 'bg-sky-50 text-sky-700',      // For vector score
            keyword: 'bg-violet-50 text-violet-700' // For keyword score
        }
    };

    return `
        <div class="${baseColors.bg} rounded-lg shadow-sm border ${baseColors.border} overflow-hidden hover:shadow-md transition-shadow duration-200 cursor-pointer"
             onclick="toggleDetails('${displayIndex}')">
            <div class="p-6">
                ${generateResultContent(match, false, displayIndex, baseColors, true, true)}
            </div>
        </div>
    `;
}

// Generate HTML for the score pills section
function generateScorePillsSection(match, pillColors) {
    const colors = typeof pillColors === 'string' ? {
        rank: pillColors,
        vector: pillColors,
        keyword: pillColors
    } : pillColors;

    return `
        <div class="flex flex-wrap gap-2">
            <span class="text-xs font-mono ${colors.rank} px-2 py-1 rounded-full flex items-center gap-1"
                  title="Combined Score">
                <svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
                </svg>
                ${match.scores.combined.toFixed(3)}
            </span>
            <span class="text-xs font-mono ${colors.vector} px-2 py-1 rounded-full flex items-center gap-1"
                  title="Vector Score">
                <svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
                </svg>
                ${match.scores.vector.toFixed(3)}
            </span>
            <span class="text-xs font-mono ${colors.keyword} px-2 py-1 rounded-full flex items-center gap-1"
                  title="Keyword Score">
                <svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M17 3a2.85 2.85 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"/>
                </svg>
                ${match.scores.keyword.toFixed(3)}
            </span>
        </div>
    `;
}

// Generate HTML for the result content
function generateResultContent(match, isExactMatch, displayIndex, baseColors, showScorePills = true, showToggleButton = true) {
    // Header Section with generic score display
    const headerSection = `
        <div class="flex justify-between items-start gap-4 mb-4">
            <div class="flex flex-col sm:flex-row sm:items-center gap-3">
                <div class="flex items-center gap-2">
                    ${generateScorePills(match.combinedScoreRank, !isExactMatch && match.isReranking, match.rank, isExactMatch)}
                </div>
                ${showScorePills ? generateScorePillsSection(match, baseColors.pill) : ''}
            </div>
            ${showToggleButton ? `
                <button
                    onclick="toggleDetails('${displayIndex}'); event.stopPropagation();"
                    class="text-gray-500 hover:text-gray-700 focus:outline-none p-2 rounded-full hover:bg-gray-100"
                    aria-label="Toggle details"
                >
                    <i data-feather="chevron-down" class="toggle-icon-${displayIndex} w-5 h-5"></i>
                </button>
            ` : ''}
        </div>
    `;

    // Metadata path display
    const metadataPath = generateMetadataPath(match.metadata);

    // Main content
    const mainContent = `
        <div class="bg-gray-50 p-4 rounded-lg">
            <p class="text-gray-900">${match.metadata[SCHEMA_CONFIG.main_content_field]}</p>
        </div>
    `;

    // Expandable details
    const expandableDetails = `
        <div class="metadata-${displayIndex} hidden mt-4">
            ${generateMetadataDetails(match.metadata)}
        </div>
    `;

    return `${headerSection}${metadataPath}${mainContent}${expandableDetails}`;
}

// Generate metadata path display
function generateMetadataPath(metadata) {
    const pathFields = SCHEMA_CONFIG.path_fields;
    if (!pathFields.length) return '';

    return `
        <div class="mb-3">
            <div class="flex flex-wrap items-center text-sm">
                ${pathFields.map((fieldConfig, index) => {
                    const value = metadata[fieldConfig.field];
                    if (fieldConfig.optional && !value) return '';
                    
                    return `
                        ${index > 0 ? `
                            <svg class="w-4 h-4 mx-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                            </svg>
                        ` : ''}
                        <span class="${fieldConfig.primary ? 'font-medium text-blue-600' : 'text-gray-600'}">
                            ${value || 'Unknown'}
                        </span>
                    `;
                }).join('')}
            </div>
        </div>
    `;
}

// Generate metadata details section
function generateMetadataDetails(metadata) {
    const config = SCHEMA_CONFIG;
    let sections = '';
    
    // Primary detail section
    if (config.primary_detail) {
        sections += `
            <div class="bg-gray-100 p-4 rounded-lg mb-4">
                <h4 class="text-sm font-medium text-gray-900 mb-2">${config.primary_detail.label}</h4>
                <p class="text-sm text-gray-800">${metadata[config.primary_detail.field] || 'N/A'}</p>
            </div>
        `;
    }

    // Secondary details grid
    if (config.secondary_details?.length > 0) {
        sections += `
            <div class="grid grid-cols-1 sm:grid-cols-${Math.min(config.secondary_details.length, 4)} gap-4">
                ${config.secondary_details.map(field => `
                    <div class="space-y-2">
                        <div class="bg-gray-50 p-3 rounded-lg">
                            <p class="text-xs text-gray-500 mb-1">${field.label}</p>
                            <p class="text-sm font-medium font-mono text-gray-700">${metadata[field.field] || 'N/A'}</p>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    return sections;
}

// Generate score pills for ranking display
function generateScorePills(combinedScoreRank, isReranking, rerankedPosition, isExactMatch) {
    const basePillClass = "text-xs font-mono px-2 py-1 rounded-full flex items-center gap-1";
    const matchPillClass = `${basePillClass} bg-rose-50 text-rose-700`;  // Same as combined score
    const rerankPillClass = `${basePillClass} bg-emerald-50 text-emerald-700`;
    
    const orderIconSvg = `<svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M3 6h18M3 12h18M3 18h18"/>
    </svg>`;
    
    const rerankIconSvg = `<svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/>
    </svg>`;

    let pills = '';
    if (isReranking) {
        pills += `<span class="${rerankPillClass}" title="Reranked Position">
            ${rerankIconSvg}
            ${rerankedPosition}
        </span>`;
    }

    // Only show the match order pill for non-exact matches
    if (!isExactMatch) {
        pills += `<span class="${matchPillClass}" title="Match Order by Combined Score">
            ${orderIconSvg}
            ${combinedScoreRank}
        </span>`;
    }

    return pills;
}

// Display exact match result
export async function displayExactMatch(match) {
    if (!match) return;
    
    const exactMatchDiv = document.getElementById('exactMatch');
    match.combinedScoreRank = 1;
    match.isExactMatch = true;
    
    exactMatchDiv.innerHTML = await generateExactMatchHTML(match);
    exactMatchDiv.classList.remove('hidden');
    feather.replace();
}

// Display regular search results
export async function displayResults(results) {
    const resultsDiv = document.getElementById('results');
    const isReranking = document.getElementById('enableReranking').checked;
    
    let displayResults = [...results];
    displayResults.sort((a, b) => b.scores.combined - a.scores.combined);
    displayResults.forEach((result, index) => {
        result.combinedScoreRank = index + 1;
        result.isReranking = isReranking;
    });
    
    if (isReranking) {
        displayResults.sort((a, b) => a.rank - b.rank);
    }
    
    // Wait for all results to be generated
    const resultHTMLPromises = displayResults.map((match, index) => 
        generateResultHTML(match, false, match.combinedScoreRank - 1)
    );
    
    const resultHTMLs = await Promise.all(resultHTMLPromises);
    resultsDiv.innerHTML = resultHTMLs.join('');
    
    feather.replace();
}

// Toggle expandable details sections
export function toggleDetails(index) {
    const metadataDiv = document.querySelector(`.metadata-${index}`);
    const toggleIcon = document.querySelector(`.toggle-icon-${index}`);
    metadataDiv.classList.toggle('hidden');

    if (metadataDiv.classList.contains('hidden')) {
        toggleIcon.setAttribute('data-feather', 'chevron-down');
    } else {
        toggleIcon.setAttribute('data-feather', 'chevron-up');
    }
    feather.replace();
}