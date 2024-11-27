import os
import time
from typing import Dict, List, Any, Optional, Tuple

from pinecone import ServerlessSpec
from pinecone.grpc import PineconeGRPC as Pinecone

from .base import BaseConnector, BaseConnectorError

class PineconeConnectorError(BaseConnectorError):
    """Specific exception class for Pinecone connector errors."""
    pass

class PineconeConnector(BaseConnector):
    """
    Connector for Pinecone vector database operations.
    Handles index management and vector operations.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Pinecone connector.
        
        Args:
            api_key: Optional API key override
            
        Raises:
            PineconeConnectorError: If initialization fails
        """
        super().__init__(env_key="PINECONE_API_KEY", api_key=api_key)
        
        # Get index name from environment
        self._index_name = os.getenv("PINECONE_INDEX_NAME")
        if not self._index_name:
            raise PineconeConnectorError("PINECONE_INDEX_NAME not found in environment variables")
            
        self._index = None
        self._search_stats = {'expansions': 0, 'total_searches': 0}

    def _initialize_client(self) -> Pinecone:
        """Initialize Pinecone client."""
        return Pinecone(api_key=self.api_key)

    @property
    def index(self) -> Any:
        """Get or create Pinecone index connection."""
        if self._index is None:
            self._index = self.client.Index(self._index_name)
        return self._index
    
    @property
    def index_name(self) -> str:
        """Get index name."""
        return self._index_name

    @property
    def expansion_rate(self) -> float:
        """Calculate percentage of searches requiring expansion."""
        if self._search_stats['total_searches'] == 0:
            return 0.0
        return (self._search_stats['expansions'] / self._search_stats['total_searches']) * 100

    def create_index(self, dimension: int, metric: str = "cosine") -> None:
        """
        Create a new Pinecone index.
        
        Args:
            dimension: Vector dimension size
            metric: Distance metric for similarity calculation
            
        Raises:
            PineconeConnectorError: If index creation fails
        """
        try:
            # Create new index
            self.client.create_index(
                name=self.index_name,
                dimension=dimension,
                metric=metric,
                spec=ServerlessSpec(cloud='aws', region='us-east-1'),
                deletion_protection="disabled"
            )
            
            # Wait for index to be ready
            while True:
                try:
                    if self.client.describe_index(self.index_name).status.get('ready'):
                        break
                except Exception:
                    pass
                time.sleep(5)
                
        except Exception as e:
            raise PineconeConnectorError(f"Failed to create index: {str(e)}") from e

    def delete_index(self) -> None:
        """
        Delete the current index.
        
        Raises:
            PineconeConnectorError: If deletion fails
        """
        try:
            if self.index_name in [index.name for index in self.client.list_indexes()]:
                self.client.delete_index(self.index_name)
                self._index = None  # Reset index reference
                time.sleep(5)  # Wait for deletion to complete
        except Exception as e:
            raise PineconeConnectorError(f"Failed to delete index: {str(e)}") from e

    def list_indexes(self) -> List[str]:
        """
        Get list of available indexes.
        
        Returns:
            List[str]: List of index names
            
        Raises:
            PineconeConnectorError: If listing fails
        """
        try:
            return [index.name for index in self.client.list_indexes()]
        except Exception as e:
            raise PineconeConnectorError(f"Failed to list indexes: {str(e)}") from e

    def get_index_stats(self, namespace: str = "") -> Dict[str, Any]:
        """
        Get statistics for current index.
        
        Args:
            namespace: Optional namespace to get stats for
            
        Returns:
            Dict[str, Any]: Index statistics
            
        Raises:
            PineconeConnectorError: If stats retrieval fails
        """
        try:
            return self.index.describe_index_stats(namespace=namespace)
        except Exception as e:
            raise PineconeConnectorError(f"Failed to get index stats: {str(e)}") from e

    def upsert_vectors(self, vectors: List[Tuple[str, List[float], Dict[str, Any]]], 
                      namespace: str = "") -> None:
        """
        Upload vectors to index.
        
        Args:
            vectors: List of (id, vector, metadata) tuples
            namespace: Optional namespace for vectors
            
        Raises:
            PineconeConnectorError: If upload fails
        """
        try:
            self.index.upsert(vectors=vectors, namespace=namespace)
        except Exception as e:
            raise PineconeConnectorError(f"Failed to upsert vectors: {str(e)}") from e

    def query_vectors(
        self,
        vector: List[float],
        top_k: int,
        include_values: bool = True,
        include_metadata: bool = True,
        filter_dict: Optional[Dict] = None,
        namespace: str = ""
    ) -> Dict[str, Any]:
        """
        Query vectors from index.
        
        Args:
            vector: Query vector
            top_k: Number of results to return
            include_values: Whether to include vector values in results
            include_metadata: Whether to include metadata in results
            filter_dict: Optional metadata filters
            namespace: Optional namespace to query
            
        Returns:
            Dict[str, Any]: Query results
            
        Raises:
            PineconeConnectorError: If query fails
        """
        try:
            self._search_stats['total_searches'] += 1
            
            return self.index.query(
                vector=vector,
                top_k=top_k,
                include_values=include_values,
                include_metadata=include_metadata,
                filter=filter_dict,
                namespace=namespace
            )
        except Exception as e:
            raise PineconeConnectorError(f"Failed to query vectors: {str(e)}") from e

# Create a global instance for convenience
pinecone_connector = PineconeConnector()