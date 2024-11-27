from typing import List, Dict, Any, Optional

import cohere

from .base import BaseConnector, BaseConnectorError

class CohereConnectorError(BaseConnectorError):
    """Specific exception class for Cohere connector errors."""
    pass

class CohereConnector(BaseConnector):
    """
    Connector for Cohere API operations.
    Handles reranking operations through Cohere's API.
    """
    
    DEFAULT_RERANK_MODEL = "rerank-english-v3.0"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Cohere connector.
        
        Args:
            api_key: Optional API key override
            
        Raises:
            CohereConnectorError: If initialization fails
        """
        super().__init__(env_key="COHERE_API_KEY", api_key=api_key)
    
    def _initialize_client(self) -> cohere.ClientV2:
        """
        Initialize Cohere client.
        
        Returns:
            cohere.ClientV2: Initialized Cohere client
            
        Raises:
            CohereConnectorError: If client initialization fails
        """
        try:
            return cohere.ClientV2(api_key=self.api_key)
        except Exception as e:
            raise CohereConnectorError(f"Failed to initialize Cohere client: {str(e)}") from e
    
    def rerank(
        self,
        query: str,
        documents: List[Dict[str, str]],
        model: str = DEFAULT_RERANK_MODEL
    ) -> Any:
        """
        Rerank documents using Cohere's API.
        
        Args:
            query: Search query
            documents: List of documents to rerank, each containing a 'text' key
            model: Model to use for reranking
            
        Returns:
            Any: Cohere reranking response
            
        Raises:
            CohereConnectorError: If reranking operation fails
        """
        if not query or not documents:
            return None
            
        try:
            return self.client.rerank(
                query=query,
                documents=documents,
                model=model
            )
        except Exception as e:
            raise CohereConnectorError(f"Reranking failed: {str(e)}") from e

# Create a global instance for convenience
cohere_connector = CohereConnector()