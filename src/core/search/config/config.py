from dataclasses import dataclass

@dataclass
class SearchConfig:
    """Configuration for hybrid search parameters.
    
    Attributes:
        vector_weight (float): Weight applied to vector similarity (0 to 1)
        keyword_weight (float): Weight applied to keyword matching (0 to 1)
        min_vector_score (float): Minimum required vector similarity score (0 to 1)
        min_keyword_score (float): Minimum required keyword matching score (0 to 1)
        min_combined_score (float): Minimum required combined score (0 to 1)
        exact_match_min_vector_score (float): Minimum vector score for exact match (0 to 1)
        exact_match_min_keyword_score (float): Minimum keyword score for exact match (0 to 1)
        initial_candidates (int): Initial number of vector search candidates
        max_candidates (int): Maximum number of vector search candidates if expansion needed
        candidate_expansion_threshold (float): Vector score threshold for expanding search
        enable_reranking (bool): Whether to enable result reranking
    """
    # Scoring weights
    vector_weight: float
    keyword_weight: float
    
    # Score thresholds for cross-framework matches
    min_vector_score: float
    min_keyword_score: float
    min_combined_score: float
    
    # Exact match thresholds
    exact_match_min_vector_score: float
    exact_match_min_keyword_score: float
    
    # Search optimization parameters
    initial_candidates: int
    max_candidates: int
    candidate_expansion_threshold: float
    
    # Reranking configuration
    enable_reranking: bool