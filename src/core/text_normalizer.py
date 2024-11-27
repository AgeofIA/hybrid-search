"""
Text Normalization Module

Provides utilities for normalizing text to ensure consistent format for search
and comparison operations. Handles:
- Converting to lowercase
- Removing punctuation
- Normalizing whitespace
- Converting hyphens to spaces

Usage:
    from text_normalizer import normalize_text
    normalized = normalize_text("Hello, World!")  # "hello world"
"""

import string
from loguru import logger


def normalize_text(text) -> str:
    """
    Normalize text for consistent processing.
    
    Args:
        text: Input text to normalize (can be None)
    
    Returns:
        Normalized text string, empty string for invalid inputs
    """
    if not _is_valid_input(text):
        return ""
        
    text = _convert_to_string(text)
    if not text:
        return ""
        
    _check_text_length(text)
    
    return _apply_normalizations(text)


def _is_valid_input(text) -> bool:
    """Check if input is valid for normalization."""
    return text is not None

def _convert_to_string(text):
    """Convert input to string and strip whitespace."""
    try:
        return str(text).strip()
    except Exception as e:
        logger.warning(f"Text normalization failed: {e}")
        return ""

def _check_text_length(text):
    """Log warning for potentially performance-impacting text length."""
    if len(text) > 1_000_000:
        logger.warning("Large text input may impact performance", size=len(text))

def _apply_normalizations(text):
    """
    Apply all text normalization rules.
    
    Returns:
        Normalized text with consistent formatting
    """
    # Convert to lowercase for case-insensitive matching
    text = text.lower()
    # Remove all punctuation except hyphens
    text = text.translate(str.maketrans("", "", string.punctuation))
    # Convert hyphens to spaces for consistent word separation
    text = text.replace('-', ' ')
    # Normalize whitespace to single spaces and strip
    return " ".join(text.split())