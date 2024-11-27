import os
from abc import ABC, abstractmethod
from typing import Optional, Any

class BaseConnectorError(Exception):
    """Base exception class for connector-related errors."""
    pass

class BaseConnector(ABC):
    """
    Abstract base class for API connectors.
    
    Provides common functionality for:
    - API key management
    - Client initialization
    - Basic error handling
    """
    
    def __init__(self, env_key: str, api_key: Optional[str] = None):
        """
        Initialize the connector.
        
        Args:
            env_key: Name of environment variable containing the API key
            api_key: Optional API key to use instead of environment variable
            
        Raises:
            BaseConnectorError: If no API key is available
        """
        self._client: Optional[Any] = None
        self._api_key = api_key or os.getenv(env_key)
        
        if not self._api_key:
            raise BaseConnectorError(f"No API key provided. Set {env_key} environment variable or pass key to constructor.")
    
    @property
    def api_key(self) -> str:
        """Get the API key."""
        return self._api_key
    
    @property
    def client(self) -> Any:
        """
        Get or create client instance with lazy initialization.
        
        Returns:
            Any: Initialized client instance
            
        Raises:
            BaseConnectorError: If client initialization fails
        """
        if self._client is None:
            try:
                self._client = self._initialize_client()
            except Exception as e:
                raise BaseConnectorError(f"Failed to initialize client: {str(e)}") from e
        return self._client
    
    @abstractmethod
    def _initialize_client(self) -> Any:
        """
        Initialize the API client.
        
        Returns:
            Any: Initialized client instance
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement _initialize_client()")