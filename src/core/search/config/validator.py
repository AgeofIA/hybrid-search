from typing import Dict, Any

REQUIRED_FIELDS = {
    # Scoring weights
    'vector_weight', 
    'keyword_weight',
    
    # Score thresholds
    'min_vector_score', 
    'min_keyword_score', 
    'min_combined_score',
    
    # Exact match thresholds
    'exact_match_min_vector_score',
    'exact_match_min_keyword_score',
    
    # Search optimization parameters
    'initial_candidates',
    'max_candidates',
    'candidate_expansion_threshold',
    
    # Reranking configuration
    'enable_reranking'
}

def validate_config_data(config_data: Dict[str, Any]) -> None:
    """Main validation function"""
    if not config_data:
        raise ValueError("No configuration data provided")
        
    _validate_required_fields(config_data)
    _validate_value_ranges(config_data)

def _validate_required_fields(config_data: Dict[str, Any]) -> None:
    """Private helper for field validation"""
    missing_fields = REQUIRED_FIELDS - set(config_data.keys())
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

def _validate_value_ranges(config_data: Dict[str, Any]) -> None:
    """Private helper for value validation"""
    for key, value in config_data.items():
        if 'weight' in key or 'score' in key:
            try:
                value = float(value)
                if not 0 <= value <= 1:
                    raise ValueError(
                        f"Invalid value for {key}. Must be between 0 and 1."
                    )
            except (ValueError, TypeError):
                raise ValueError(f"Invalid value for {key}. Must be a number.")

        # Validate integer parameters
        elif key in {'initial_candidates', 'max_candidates'}:
            try:
                value = int(value)
                if value <= 0:
                    raise ValueError(f"{key} must be positive")
            except (ValueError, TypeError):
                raise ValueError(f"Invalid value for {key}. Must be a positive integer.")