"""
Search Result Reranking Module

Handles semantic reranking of search results using Cohere's API to improve 
relevance based on contextual understanding.
"""

from loguru import logger

from .exceptions import RerankingError
from connectors.cohere import cohere_connector, CohereConnectorError


def rerank_results(query: str, results: list, metadata_schema) -> list:
    """
    Rerank search results using semantic understanding.
    
    Args:
        query: Search query string
        results: List of dictionaries containing:
            - metadata: Dict with result metadata
            - scores: Original relevance scores
        metadata_schema: Schema for processing metadata
        
    Returns:
        Reranked list of results with original data preserved
        
    Raises:
        RerankingError: If reranking fails due to invalid input or API errors
    """
    if not _validate_inputs(query, results):
        return results

    with logger.contextualize(query=query, result_count=len(results)):
        try:
            documents = _prepare_documents(results, metadata_schema)
            if not documents:
                logger.warning("No valid documents to rerank")
                return results
            
            rerank_response = cohere_connector.rerank(
                query=query,
                documents=documents
            )
            
            reranked = [
                results[result.index] 
                for result in rerank_response.results
            ]
            
            logger.debug(
                "Reranking completed",
                original_count=len(results),
                reranked_count=len(reranked)
            )
            return reranked
            
        except CohereConnectorError as e:
            logger.error("Reranking API call failed", error=str(e))
            raise RerankingError(
                "Failed to rerank results", 
                details={'error': str(e)}
            ) from e
        except Exception as e:
            logger.error("Unexpected reranking error", error=str(e))
            raise RerankingError(
                "Unexpected error during reranking",
                details={'error': str(e)}
            ) from e


def _validate_inputs(query: str, results: list) -> bool:
    """Validate reranking input parameters."""
    if not query or not isinstance(query, str):
        raise RerankingError("Query must be a non-empty string")
        
    if not results or not isinstance(results, list):
        logger.debug("No valid results provided")
        return False
        
    return True


def _prepare_documents(results: list, metadata_schema) -> list:
    """
    Prepare search results for reranking.
    
    Args:
        results: List of search result dictionaries
        metadata_schema: Schema for processing metadata
        
    Returns:
        List of documents prepared for reranking
    """
    documents = []
    
    for result in results:
        if not isinstance(result, dict) or 'metadata' not in result:
            logger.warning("Invalid result format, skipping", result=result)
            continue
            
        try:
            metadata = metadata_schema.process(result['metadata'])
            documents.append({"text": metadata.text})
            
        except ValueError as e:
            logger.warning(
                "Skipping invalid metadata", 
                error=str(e)
            )
            continue
            
    return documents