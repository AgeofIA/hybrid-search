"""
Search Manager Module

Handles search request processing and result formatting.

Components:
    - Request validation
    - Query processing
    - Search execution
    - Result formatting
"""

from loguru import logger

from .exceptions import SearchValidationError, SearchExecutionError
from .response_formatter import format_search_response
from .hybridizer import hybrid_search
from .reranker import rerank_results
from embedder import create_embedding, EmbeddingError
from text_normalizer import normalize_text
from metadata import metadata_schema


class SearchManager:
    """Manages search operations and result formatting."""
    
    def __init__(self, search_client, config_manager):
        """Initialize with search client and config manager."""
        self.search_client = search_client
        self.config_manager = config_manager
        self.metadata_schema = metadata_schema
        logger.info("SearchManager initialized")

    def execute_search(self, request_data: dict) -> tuple[dict, int]:
        """
        Execute search operation and handle request lifecycle.
        
        Args:
            request_data: Raw request data containing query and optional config
                
        Returns:
            Tuple[dict, int]: Response data and HTTP status code
        """
        try:
            query, search_config = self.validate_search_request(request_data)
            
            with logger.contextualize(query=query):
                logger.info("Executing search")
                
                processed_query = self._validate_query(query)
                
                # Handle optional search configuration updates
                if search_config:
                    search_config = self.config_manager.update_config(search_config)
                else:
                    search_config = self.config_manager.get_config()
                
                # Generate query embedding and tokens
                query_embedding, query_tokens = self._process_query(processed_query)
                
                # Execute hybrid search with metadata schema
                results = hybrid_search(
                    query_vector=query_embedding,
                    query_tokens=query_tokens,
                    config=search_config,
                    metadata_schema=self.metadata_schema,
                    group_by=self.metadata_schema.group_by_field
                )

                # Rerank if enabled
                if search_config.enable_reranking:
                    results['matches'] = rerank_results(
                        query=processed_query,
                        results=results['matches'],
                        metadata_schema=self.metadata_schema
                    )

                logger.info("Search completed successfully")
                response = format_search_response(
                    results,
                    query,
                    normalize_text(query)
                )
                return response, 200
                
        except ValueError as e:
            raise SearchValidationError(str(e), field='config')
        except EmbeddingError as e:
            raise SearchExecutionError("Failed to process query", {'error': str(e)})
        except Exception as e:
            # Log the actual error before converting to SearchExecutionError
            logger.error(f"Search execution failed: {str(e)}", exc_info=True)
            raise SearchExecutionError("Search execution failed", {'error': str(e)})

    def validate_search_request(self, data: dict) -> tuple[str, dict]:
        """
        Validate search request data and extract query and config.
        
        Args:
            data: Raw request data containing query and optional config
            
        Returns:
            Tuple of (query string, optional config dict)
            
        Raises:
            SearchValidationError: If request data is invalid
        """
        if not data:
            raise SearchValidationError("No search data provided")
                
        query = data.get('query', '').strip()
        if not query:
            raise SearchValidationError("Search query is required", field='query')
                
        return query, data.get('config', {})

    def _validate_query(self, query):
        """Validate and clean search query."""
        if not query or not query.strip():
            raise SearchValidationError("Query cannot be empty", field='query')
                
        processed = query.strip()
        if len(processed) < 3:
            raise SearchValidationError("Query must be at least 3 characters", field='query')
                
        return processed

    def _process_query(self, query):
        """
        Process query into embedding and tokens.
        
        Returns:
            Tuple of (query_embedding, query_tokens)
        
        Raises:
            SearchExecutionError: If query processing fails
        """
        try:
            normalized_query = normalize_text(query)
            query_embedding = create_embedding(normalized_query)
            query_tokens = normalized_query.split()
                
            return query_embedding, query_tokens
                
        except Exception as e:
            raise SearchExecutionError(
                "Failed to process query",
                {'error': str(e), 'query': query}
            )