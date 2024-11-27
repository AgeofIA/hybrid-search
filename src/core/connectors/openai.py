import os
from typing import Dict, List, Optional

from openai import OpenAI, BadRequestError

from .base import BaseConnector, BaseConnectorError

class OpenAIConnectorError(BaseConnectorError):
    """Specific exception class for OpenAI connector errors."""
    pass

class OpenAIConnector(BaseConnector):
    """Connector for OpenAI API interactions."""
    
    # Supported embedding models and their configurations
    MODEL_CONFIGS: Dict[str, Dict[str, int]] = {
        "text-embedding-3-small": {
            "dimensions": 1536
        },
        "text-embedding-3-large": {
            "dimensions": 3072
        }
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenAI connector with configuration.
        
        Args:
            api_key: Optional API key override
            
        Raises:
            OpenAIConnectorError: If configuration is invalid
        """
        super().__init__(env_key="OPENAI_API_KEY", api_key=api_key)
        self._initialize_model_config()
    
    def _initialize_client(self) -> OpenAI:
        """Initialize OpenAI client."""
        return OpenAI(api_key=self.api_key)
    
    def _initialize_model_config(self) -> None:
        """
        Initialize model configuration.
        
        Raises:
            OpenAIConnectorError: If model configuration is invalid
        """
        self.model_name = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        
        if self.model_name not in self.MODEL_CONFIGS:
            raise OpenAIConnectorError(f"Unsupported embedding model: {self.model_name}")
    
    @property
    def dimensions(self) -> int:
        """Get embedding dimensions for current model."""
        return self.MODEL_CONFIGS[self.model_name]["dimensions"]
    
    def create_embeddings(self, input_texts: List[str]) -> List[List[float]]:
        """
        Create embeddings for text input.
        
        Args:
            input_texts: Single text or list of texts for embedding
            
        Returns:
            List[List[float]]: List of embedding vectors
            
        Raises:
            OpenAIConnectorError: If embedding creation fails
        """
        try:
            response = self.client.embeddings.create(
                model=self.model_name,
                input=input_texts
            )
            return [item.embedding for item in response.data]
            
        except BadRequestError as e:
            self._handle_api_error(e)
    
    def _handle_api_error(self, error: BadRequestError, context: str = "") -> None:
        """
        Handle OpenAI API errors with context.
        
        Args:
            error: The API error
            context: Additional context for the error
            
        Raises:
            OpenAIConnectorError: Wrapped API error with context
        """
        error_msg = str(error)
        prefix = f"{context}: " if context else ""
        
        if "pattern" in error_msg.lower():
            raise OpenAIConnectorError(
                f"{prefix}Invalid characters in text. Please use standard text only."
            ) from error
        raise OpenAIConnectorError(f"{prefix}API error: {error_msg}") from error

# Create a global instance for convenience
openai_connector = OpenAIConnector()