from dataclasses import dataclass
from typing import Any, Dict, List

@dataclass
class BaseMetadata:
    """Base metadata container with required fields for search functionality."""
    id: str  # Unique identifier
    text: str  # Original text content
    normalized_text: str  # Normalized text for searching

class MetadataSchema:
    """Base class for metadata schemas."""
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """
        Validate metadata against schema requirements.
        
        Args:
            data: Dictionary of metadata to validate
            
        Returns:
            bool: Whether the metadata is valid
            
        Raises:
            ValueError: If validation fails with specific reason
        """
        raise NotImplementedError
    
    def process(self, data: Dict[str, Any]) -> BaseMetadata:
        """
        Process raw metadata into standardized format.
        
        Args:
            data: Raw metadata dictionary
            
        Returns:
            BaseMetadata: Processed metadata instance
            
        Raises:
            ValueError: If processing fails
        """
        raise NotImplementedError
    
    def get_csv_header_fields(self) -> List[str]:
        """Get fields for CSV header."""
        raise NotImplementedError
        
    def format_csv_row(
        self, 
        source_metadata: BaseMetadata, 
        target_metadata: BaseMetadata,
        rank: int,
        scores: Dict[str, float]
    ) -> List[Any]:
        """Format metadata for CSV output."""
        raise NotImplementedError