"""
Keyword Search Module

Handles text-based search operations using token matching and exact phrase matching.
Supports both general token matching and exact phrase detection.

Components:
    - keyword_search: Main search function for calculating match scores

Usage:
    from search.keyword_searcher import keyword_search
    
    score = keyword_search(
        query_tokens=['secure', 'password'],
        doc_tokens=['secure', 'password', 'required']
    )
"""

from typing import List

from loguru import logger


def keyword_search(query_tokens: List[str], doc_tokens: List[str]) -> float:
    """
    Calculate keyword matching score between query and document.
    
    Args:
        query_tokens: List of normalized tokens from search query
        doc_tokens: List of normalized tokens from document
        
    Returns:
        float: Final keyword matching score between 0 and 1
        
    Example:
        score = keyword_search(
            query_tokens=['secure', 'password'],
            doc_tokens=['secure', 'password', 'required']
        )
    """
    if not query_tokens or not doc_tokens:
        logger.debug("Empty tokens provided, returning 0 score")
        return 0.0
        
    # Get base token matching score
    base_score, matches = _tokenize_and_match(query_tokens, doc_tokens)
    
    # Check for exact phrase matches
    query_text = " ".join(query_tokens)
    doc_text = " ".join(doc_tokens)
    
    if _check_exact_matches(query_text, doc_text):
        logger.debug("Exact match found", query=query_text)
        return 1.0
            
    logger.debug("Partial match score", score=base_score, matches=matches)
    return base_score


def _tokenize_and_match(query_tokens, doc_tokens):
    """Internal helper for token matching."""
    if not query_tokens or not doc_tokens:
        return 0.0, 0
    
    query_set = set(query_tokens)
    doc_set = set(doc_tokens)
    matching_tokens = query_set.intersection(doc_set)
    
    base_score = len(matching_tokens) / len(query_set)
    return base_score, len(matching_tokens)

def _check_exact_matches(query_text, doc_text):
    """Internal helper for exact phrase matching."""
    return query_text in doc_text