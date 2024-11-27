"""
Hybrid Search Module

Implements hybrid search combining vector similarity, keyword matching,
and optional semantic reranking. Provides configurable thresholds and
weights for each search component.

Components:
    - hybrid_search: Main search function combining multiple search strategies
"""

from typing import List, Dict, Any, Optional

from loguru import logger

from .config import SearchConfig
from .exceptions import VectorSearchError
from .vector_searcher import vector_search
from .keyword_searcher import keyword_search
from .reranker import rerank_results

# Configure module logger with context
logger = logger.bind(module="hybrid_search")


def hybrid_search(
    query_vector: List[float],
    query_tokens: List[str],
    config: SearchConfig,
    metadata_schema,
    content_field: str = 'normalized_text',
    group_by: Optional[str] = None
) -> Dict[str, Any]:
    """
    Perform hybrid search combining vector similarity and keyword matching.
    
    Args:
        query_vector: Embedded query vector for similarity search
        query_tokens: Tokenized query for keyword matching
        config: Search configuration parameters
        metadata_schema: Schema for processing metadata
        content_field: Name of metadata field containing normalized text content
        group_by: Optional metadata field to group results by
        
    Returns:
        Dict containing:
        - exact_match: Exact match result if found
        - matches: Results grouped by group_by field if specified
        - metadata: Search statistics and configuration
        
    Raises:
        VectorSearchError: If vector search fails
    """
    logger.info("Starting hybrid search", query_length=len(query_tokens))
    
    # First try to find exact match
    exact_match = _find_exact_match(
        query_vector, 
        query_tokens, 
        config, 
        metadata_schema, 
        content_field
    )
    exclude_value = exact_match['metadata'].get(group_by) if exact_match and group_by else None
    
    try:
        # Perform vector search excluding source group if exact match found
        vector_results, search_stats = vector_search(
            query_vector=query_vector,
            config=config,
            exclude_field=group_by,
            exclude_value=exclude_value
        )
        
        qualifying_results = []
        group_counts = {}
        
        # Process and filter results meeting thresholds
        for result in vector_results:
            processed = _process_result(
                result, 
                query_tokens, 
                config, 
                metadata_schema, 
                content_field
            )
            if processed is None:
                continue
                
            scores = processed['scores']
            
            if _meets_thresholds(scores, config):
                if group_by:
                    group = processed['metadata'].get(group_by, 'unknown')
                    group_counts[group] = group_counts.get(group, 0) + 1
                qualifying_results.append(processed)
        
        # Apply reranking if enabled and we have results
        if config.enable_reranking and qualifying_results:
            query = " ".join(query_tokens)
            qualifying_results = rerank_results(
                query=query,
                results=qualifying_results,
                metadata_schema=metadata_schema
            )
        
        # Group results if grouping field specified
        results_data = (
            _group_results(qualifying_results, group_by)
            if group_by else qualifying_results
        )
        
        logger.info(
            "Search completed",
            total_results=len(qualifying_results),
            groups=len(group_counts) if group_by else 0
        )
        
        metadata = {
            'total_candidates': len(vector_results),
            'qualifying_matches': len(qualifying_results),
            'thresholds': {
                'min_vector_score': config.min_vector_score,
                'min_keyword_score': config.min_keyword_score,
                'min_combined_score': config.min_combined_score
            }
        }
        
        # Add group-specific metadata if grouping was used
        if group_by:
            metadata.update({
                'groups_found': list(group_counts.keys()),
                'matches_per_group': group_counts,
                'source_group': exclude_value
            })
        
        return {
            'exact_match': exact_match,
            'matches': results_data,
            'metadata': metadata
        }
        
    except VectorSearchError as e:
        logger.error("Vector search failed", error=str(e))
        raise


def _process_result(result, query_tokens, config, metadata_schema, content_field):
    """Process single search result with combined scoring."""
    try:
        # Process metadata through provided schema
        metadata = metadata_schema.process(result['metadata'])
        
        # Get normalized text from metadata
        doc_text = metadata.normalized_text
        doc_tokens = doc_text.split()
        
        vector_score = result['score']
        keyword_score = keyword_search(query_tokens, doc_tokens)
        combined_score = _combine_scores(vector_score, keyword_score, config)
        
        return {
            'id': metadata.id,
            'metadata': metadata_schema.to_search_metadata(metadata),
            'scores': {
                'combined': combined_score,
                'vector': vector_score,
                'keyword': keyword_score
            }
        }
    except ValueError as e:
        logger.warning(f"Invalid metadata in result: {str(e)}")
        return None


def _combine_scores(vector_score, keyword_score, config):
    """Calculate weighted combination of scores."""
    return (
        config.vector_weight * vector_score +
        config.keyword_weight * keyword_score
    )


def _find_exact_match(query_vector, query_tokens, config, metadata_schema, content_field):
    """Find exact match through text or high similarity."""
    query_text = " ".join(query_tokens)
    
    try:
        vector_results, _ = vector_search(
            query_vector=query_vector,
            config=config
        )
        if not vector_results:
            return None
            
        # Check top results for exact matches
        for result in vector_results[:5]:
            processed = _process_result(
                result, 
                query_tokens, 
                config, 
                metadata_schema, 
                content_field
            )
            if not processed:
                continue
                
            metadata = metadata_schema.process(processed['metadata'])
            if metadata.normalized_text == query_text:
                logger.info("Found exact text match")
                return processed
                
            if _meets_exact_thresholds(processed['scores'], config):
                logger.info("Found similarity threshold match")
                return processed
                
    except VectorSearchError as e:
        logger.error("Vector search failed during exact match check", error=str(e))
        return None
    
    return None


def _meets_thresholds(scores, config):
    """Check if scores meet minimum thresholds."""
    return (
        scores['vector'] >= config.min_vector_score and
        scores['keyword'] >= config.min_keyword_score and
        scores['combined'] >= config.min_combined_score
    )


def _meets_exact_thresholds(scores, config):
    """Check if scores meet exact match thresholds."""
    return (
        scores['vector'] >= config.exact_match_min_vector_score and
        scores['keyword'] >= config.exact_match_min_keyword_score
    )


def _group_results(results, group_by):
    """Group results by specified metadata field."""
    if not group_by:
        return results
        
    grouped = {}
    for result in results:
        group = result['metadata'].get(group_by, 'unknown')
        if group not in grouped:
            grouped[group] = []
        grouped[group].append(result)
    return grouped