"""
Vector Search Module

Handles similarity search operations using Pinecone vector database.
Includes automatic result expansion when high-quality matches are found.

Components:
    - vector_search: Main search function with expansion logic
    - SearchError: Custom exception for search operations

Dependencies:
    - SearchConfig: Configuration class imported from .config module
    - pinecone_connector: Database connector for vector operations

Usage:
    from search.vector_searcher import vector_search
    from search.config import SearchConfig
    
    results, stats = vector_search(
        query_vector=[0.1, 0.2, ...], 
        config=SearchConfig(initial_candidates=50),
        exclude_field='category',
        exclude_value='sample'
    )
"""

from typing import List, Dict, Any, Tuple, Optional

from loguru import logger

from .config import SearchConfig
from .exceptions import VectorSearchError
from connectors.pinecone import pinecone_connector


# Global statistics tracker
_search_stats = {'expansions': 0, 'total_searches': 0}


def vector_search(
    query_vector: List[float],
    config: SearchConfig,
    exclude_field: Optional[str] = None,
    exclude_value: Optional[str] = None
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Perform vector similarity search with automatic result expansion.
    
    Args:
        query_vector: Embedded query vector for similarity search
        config: Search configuration parameters including:
            - initial_candidates: Initial number of results to fetch
            - max_candidates: Maximum results after expansion
            - candidate_expansion_threshold: Score threshold for expansion
        exclude_field: Optional metadata field to use for exclusion filtering
        exclude_value: Optional value to exclude for the specified field
        
    Returns:
        Tuple containing:
        - List of search matches with scores and metadata
        - Statistics about the search operation
        
    Raises:
        SearchError: If search operation fails
        
    Example:
        results, stats = vector_search(
            query_vector=[0.1, 0.2, ...],
            config=SearchConfig(initial_candidates=50),
            exclude_field='category',
            exclude_value='test'
        )
    """
    global _search_stats
    _search_stats['total_searches'] += 1
    
    logger.debug(
        "Starting vector search",
        exclude_field=exclude_field,
        exclude_value=exclude_value
    )
    
    try:
        results, stats = _perform_initial_search(
            query_vector, config, exclude_field, exclude_value
        )
        
        if _should_expand_results(results['matches'], config.candidate_expansion_threshold):
            results, stats = _perform_expanded_search(
                query_vector, config, exclude_field, exclude_value
            )
        
        logger.info(
            "Search completed",
            candidates=len(results['matches']),
            expanded=stats['expanded_search']
        )
        return results['matches'], stats
        
    except Exception as e:
        logger.error("Search failed", error=str(e))
        raise VectorSearchError(f"Vector search failed: {str(e)}") from e


def _perform_initial_search(query_vector, config, exclude_field, exclude_value):
    """Execute initial search with basic configuration."""
    results = _execute_search(
        query_vector,
        config.initial_candidates,
        exclude_field,
        exclude_value
    )
    
    return results, {
        'initial_candidates': len(results['matches']),
        'expanded_search': False
    }


def _perform_expanded_search(query_vector, config, exclude_field, exclude_value):
    """Execute expanded search with increased candidates."""
    global _search_stats
    _search_stats['expansions'] += 1
    logger.info("Expanding search results due to high match quality")
    
    results = _execute_search(
        query_vector,
        config.max_candidates,
        exclude_field,
        exclude_value
    )
    
    return results, {
        'expanded_search': True,
        'total_candidates': len(results['matches'])
    }


def _execute_search(
    query_vector: List[float],
    top_k: int,
    exclude_field: Optional[str] = None,
    exclude_value: Optional[str] = None
) -> Dict[str, Any]:
    """
    Execute vector search with given parameters.
    
    Args:
        query_vector: Vector to search for
        top_k: Number of results to fetch
        exclude_field: Optional metadata field for exclusion
        exclude_value: Optional value to exclude
        
    Returns:
        Dict containing search results and metadata
    """
    filter_dict = None
    if exclude_field and exclude_value is not None:
        filter_dict = {exclude_field: {"$ne": exclude_value}}
    
    return pinecone_connector.query_vectors(
        vector=query_vector,
        top_k=top_k,
        include_values=True,
        include_metadata=True,
        filter_dict=filter_dict
    )


def _should_expand_results(matches: List[Dict[str, Any]], threshold: float) -> bool:
    """
    Determine if results should be expanded based on match quality.
    
    Args:
        matches: List of search matches
        threshold: Score threshold for expansion
        
    Returns:
        bool: Whether to expand search results
    """
    min_score = min(match['score'] for match in matches)
    return min_score > threshold