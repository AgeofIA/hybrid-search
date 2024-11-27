"""
Text Embedding Module

Handles text embedding generation using OpenAI's API. Provides both
single text and batch processing capabilities with automatic text
normalization.

Required Configuration:
    OpenAI API configuration must be set in environment variables.
    See openai_connector documentation for details.

Usage:
    from embedder import create_embedding, create_batch_embeddings
    
    # Single text embedding
    embedding = create_embedding("Sample text")
    
    # Batch processing
    embeddings = create_batch_embeddings(["Text 1", "Text 2"])
"""

from typing import List

from loguru import logger

from connectors.openai import openai_connector, OpenAIConnectorError
from text_normalizer import normalize_text


class EmbeddingError(Exception):
    """Base exception for embedding-related errors."""
    pass


def create_embedding(text: str) -> List[float]:
    """
    Create embedding for a single text.
    
    Args:
        text: Text to create embedding for
        
    Returns:
        List[float]: Embedding vector
        
    Raises:
        EmbeddingError: If text is invalid or processing fails
    """
    try:
        normalized_text = _validate_text(text)
        embeddings = openai_connector.create_embeddings([normalized_text])
        return embeddings[0]
        
    except OpenAIConnectorError as e:
        logger.error("Embedding creation failed", error=str(e))
        raise EmbeddingError(f"Processing failed: {str(e)}")


def create_batch_embeddings(texts: List[str], batch_size: int = 100) -> List[List[float]]:
    """
    Create embeddings for multiple texts with batching.
    
    Args:
        texts: List of texts to create embeddings for
        batch_size: Number of texts to process in each batch
        
    Returns:
        List[List[float]]: List of embedding vectors
        
    Raises:
        EmbeddingError: If texts are invalid or processing fails
    """
    # Input validation
    if not texts:
        raise EmbeddingError("No texts provided")
    
    logger.info("Processing batch embeddings", total_texts=len(texts))
    
    # Normalize and validate all input texts
    normalized_texts = _normalize_text_batch(texts)
    if not normalized_texts:
        raise EmbeddingError("No valid texts after normalization")
    
    return _process_embedding_batches(normalized_texts, batch_size)

def _validate_text(text):
    """
    Validate and normalize input text.
    
    Args:
        text: Input text to validate and normalize
        
    Returns:
        str: Normalized text
        
    Raises:
        EmbeddingError: If text is invalid
    """
    if not text or not text.strip():
        raise EmbeddingError("Empty text provided")
        
    normalized = normalize_text(text)
    if not normalized or not normalized.strip():
        raise EmbeddingError("Text is empty after normalization")
        
    return normalized

def _normalize_text_batch(texts):
    """
    Normalize a batch of texts, skipping invalid ones.
    
    Args:
        texts: List of texts to normalize
        
    Returns:
        List[str]: List of normalized texts
    """
    normalized_texts = []
    for text in texts:
        try:
            normalized = _validate_text(text)
            normalized_texts.append(normalized)
        except EmbeddingError:
            logger.warning("Skipping invalid text", text_preview=text[:50])
    return normalized_texts


def _process_embedding_batches(texts, batch_size):
    """
    Process texts in batches to create embeddings.
    
    Args:
        texts: List of texts to process
        batch_size: Size of each batch
        
    Returns:
        List[List[float]]: List of embedding vectors
        
    Raises:
        EmbeddingError: If batch processing fails
    """
    all_embeddings = []
    total_batches = (len(texts) + batch_size - 1) // batch_size
    
    # Process texts in batches
    for i in range(0, len(texts), batch_size):
        # Prepare current batch
        batch = texts[i:i + batch_size]
        batch_num = i // batch_size + 1
        
        try:
            # Create embeddings for current batch
            logger.info("Processing batch", batch_num=batch_num, total=total_batches)
            batch_embeddings = openai_connector.create_embeddings(batch)
            all_embeddings.extend(batch_embeddings)
            
        except OpenAIConnectorError as e:
            logger.error("Batch processing failed", 
                       batch_num=batch_num,
                       total=total_batches,
                       error=str(e))
            raise EmbeddingError(f"Batch {batch_num}/{total_batches} failed: {str(e)}")
    
    return all_embeddings