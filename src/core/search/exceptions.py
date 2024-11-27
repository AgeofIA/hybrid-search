"""
Search System Exceptions

Contains all custom exceptions used by the search system components.
Provides a consistent hierarchy for error handling across the search
functionality.

Exception Hierarchy:
    SearchError
    ├── SearchValidationError
    ├── SearchExecutionError
    ├── VectorSearchError
    ├── RerankingError
    └── ResponseFormattingError

Usage:
    from search.exceptions import SearchValidationError, RerankingError
    
    if not query:
        raise SearchValidationError("Query cannot be empty", field="query")
        
    if reranking_failed:
        raise RerankingError("Cannot rerank results")
"""

class SearchError(Exception):
    """Base exception for all search-related errors."""
    def __init__(self, message: str, details: dict = None):
        self.details = details or {}
        super().__init__(message)


class SearchValidationError(SearchError):
    """
    Raised when search request validation fails.
    
    Attributes:
        message: Error description
        field: Optional field name that failed validation
        details: Additional error context
    """
    def __init__(self, message: str, field: str = None, details: dict = None):
        self.field = field
        super().__init__(message, details)
        self.status_code = 400


class SearchExecutionError(SearchError):
    """
    Raised when search execution fails.
    
    Used for runtime errors during search operations including:
    - Database errors
    - Processing failures
    - External service failures
    
    Attributes:
        message: Error description
        details: Additional error context including stack traces
    """
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, details)
        self.status_code = 500


class VectorSearchError(SearchError):
    """
    Raised when vector search operations fail.
    
    Used to encapsulate all vector search-related failures including:
    - Database connection errors
    - Query validation failures
    - Result processing errors
    
    Attributes:
        message: Error description
        details: Optional dictionary with error context
        status_code: HTTP status code (defaults to 500)
    """
    def __init__(self, message: str, details: dict = None, status_code: int = 500):
        self.status_code = status_code
        super().__init__(message, details)


class RerankingError(SearchError):
    """
    Raised when reranking operations fail.
    
    Used for failures during the reranking process including:
    - Invalid input data
    - Missing required fields
    - API communication errors
    - Result processing failures
    
    Attributes:
        message: Error description
        details: Additional error context
    """
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, details)
        self.status_code = 500


class ResponseFormattingError(SearchError):
    """
    Raised when search response formatting fails.
    
    Used when the search results cannot be properly formatted into
    the expected response structure. Common causes include:
    - Missing required fields in results
    - Invalid data types
    - Structural mismatches
    
    Attributes:
        message: Error description
        details: Additional context about the formatting failure
        status_code: HTTP status code (defaults to 500)
    """
    def __init__(self, message: str, details: dict = None, status_code: int = 500):
        self.status_code = status_code
        super().__init__(message, details)