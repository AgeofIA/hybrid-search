"""
Response Formatting Module

Provides utilities for formatting search results and error messages into
standardized response structures for the search API.

Public Functions:
    format_search_response: Format complete search results
    format_error_response: Format error responses
"""

from typing import Dict, Any
from loguru import logger

from .exceptions import ResponseFormattingError


def format_search_response(results: Dict[str, Any], query: str, normalized_query: str) -> Dict[str, Any]:
    """
    Format complete search response with results and metadata.
    
    Args:
        results: Raw search results from search client
        query: Original search query
        normalized_query: Normalized version of search query
        
    Returns:
        Dictionary containing formatted search response
        
    Raises:
        ResponseFormattingError: If results cannot be formatted properly
    """
    try:
        response = _create_base_response(results, query, normalized_query)
        matches = results.get('matches', {})

        # Handle both grouped and ungrouped results
        if isinstance(matches, dict):
            response['matches'] = _process_grouped_matches(matches)
            match_count = sum(len(group) for group in matches.values())
            group_count = len(matches)
        else:
            response['matches'] = _process_ungrouped_matches(matches)
            match_count = len(matches)
            group_count = 0

        logger.info(
            "Response formatted",
            matches=match_count,
            groups=group_count
        )
        
        return response

    except (KeyError, TypeError, AttributeError) as e:
        logger.error("Response formatting failed", error=str(e))
        raise ResponseFormattingError(f"Failed to format search response: {str(e)}")


def _create_base_response(results: Dict[str, Any], query: str, normalized_query: str) -> Dict[str, Any]:
    """
    Create the base response structure with metadata.
    
    Args:
        results: Raw search results
        query: Original query
        normalized_query: Normalized query
        
    Returns:
        Base response structure with metadata
    """
    metadata = results['metadata']
    response = {
        'exact_match': results.get('exact_match'),
        'matches': [],
        'search_metadata': {
            'query': query,
            'normalized_query': normalized_query,
            'total_candidates': metadata['total_candidates'],
            'total_qualifying_matches': metadata['qualifying_matches'],
            'thresholds': metadata['thresholds'],
            'reranking_enabled': metadata.get('reranking_enabled', False)
        }
    }

    # Add group-specific metadata if present
    if 'groups_found' in metadata:
        response['search_metadata'].update({
            'groups_found': metadata['groups_found'],
            'matches_per_group': metadata['matches_per_group'],
            'source_group': metadata.get('source_group')
        })

    return response


def _process_grouped_matches(grouped_matches: Dict[str, list]) -> list:
    """
    Process and rank matches that are grouped.
    
    Args:
        grouped_matches: Dictionary of matches grouped by category
        
    Returns:
        List of formatted and ranked matches
    """
    processed_matches = []
    rank = 1

    for group, matches in grouped_matches.items():
        for match in matches:
            formatted_match = {
                'id': match['id'],
                'scores': match['scores'],
                'metadata': match['metadata'],
                'rank': rank,
                'group': group
            }
            processed_matches.append(formatted_match)
            rank += 1

    return processed_matches


def _process_ungrouped_matches(matches: list) -> list:
    """
    Process and rank ungrouped matches.
    
    Args:
        matches: List of match results
        
    Returns:
        List of formatted and ranked matches
    """
    return [
        {
            'id': match['id'],
            'scores': match['scores'],
            'metadata': match['metadata'],
            'rank': index + 1
        }
        for index, match in enumerate(matches)
    ]