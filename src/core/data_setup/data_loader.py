import json
import pandas as pd
from tqdm.auto import tqdm
import os
from dotenv import load_dotenv

from connectors.openai import openai_connector
from connectors.pinecone import pinecone_connector
from metadata import metadata_schema

# Load environment variables
load_dotenv()

# Constants
BATCH_SIZE = 100
DEFAULT_NAMESPACE = ""
EMBEDDINGS_COLUMN = 'embedding_vector'
NORMALIZED_TEXT_COLUMN = 'normalized_statement'

class DataUploadError(Exception):
    """Base exception for data upload errors."""
    pass

def prepare_vector_metadata(row: pd.Series) -> dict:
    """
    Prepare metadata using custom schema.
    
    Args:
        row: DataFrame row containing metadata fields
        
    Returns:
        dict: Processed metadata ready for vector storage
        
    Raises:
        DataUploadError: If metadata processing fails
    """
    try:
        # Convert row to dictionary for schema processing
        row_dict = row.to_dict()
        
        # Process metadata using custom schema
        metadata = metadata_schema.process(row_dict)
        
        # Convert to search-compatible format
        return metadata_schema.to_search_metadata(metadata)
        
    except Exception as e:
        raise DataUploadError(f"Failed to prepare metadata: {str(e)}")

def upload_to_pinecone(csv_path: str, recreate_index: bool = False):
    """
    Upload embeddings to Pinecone index.
    
    Args:
        csv_path: Path to CSV file containing data and embeddings
        recreate_index: Whether to recreate the Pinecone index
        
    Raises:
        DataUploadError: If upload process fails
    """
    try:
        # Get embedding dimension from OpenAI connector
        embedding_dim = openai_connector.dimensions
        
        # Handle index creation/recreation
        if recreate_index:
            if pinecone_connector.index_name in pinecone_connector.list_indexes():
                print(f"Deleting existing index: {pinecone_connector.index_name}")
                pinecone_connector.delete_index()
                
            print(f"Creating new index: {pinecone_connector.index_name}")
            pinecone_connector.create_index(dimension=embedding_dim)
        
        # Load data
        print("\nLoading data from CSV...")
        df = pd.read_csv(csv_path)
        print(f"Loaded {len(df)} rows")
        
        # Upload vectors in batches
        print("\nUploading vectors to Pinecone...")
        failed_batches = 0
        vector_id = 1
        
        for i in tqdm(range(0, len(df), BATCH_SIZE)):
            batch_df = df.iloc[i:i + BATCH_SIZE]
            vectors = []
            
            for _, row in batch_df.iterrows():
                try:
                    if pd.isna(row[EMBEDDINGS_COLUMN]):
                        continue
                        
                    # Prepare vector metadata
                    metadata = prepare_vector_metadata(row)
                    
                    vectors.append((
                        str(vector_id),
                        json.loads(row[EMBEDDINGS_COLUMN]),
                        metadata
                    ))
                    vector_id += 1
                except Exception as e:
                    print(f"\nError preparing vector: {str(e)}")
                    continue
            
            if vectors:
                try:
                    pinecone_connector.upsert_vectors(vectors, namespace=DEFAULT_NAMESPACE)
                except Exception as e:
                    print(f"\nError uploading batch: {str(e)}")
                    failed_batches += 1
        
        # Print results
        print("\nUpload complete!")
        if failed_batches:
            print(f"Warning: {failed_batches} batches failed to upload")
        
        # Show final stats
        stats = pinecone_connector.get_index_stats(namespace=DEFAULT_NAMESPACE)
        print(f"Total vectors in index: {stats.total_vector_count}")
        
    except Exception as e:
        raise DataUploadError(f"Upload process failed: {str(e)}")

if __name__ == "__main__":
    try:
        csv_path = os.getenv('DATA_CSV_PATH')
        if not csv_path:
            raise ValueError("DATA_CSV_PATH not found in environment variables")
            
        upload_to_pinecone(
            csv_path=csv_path,
            recreate_index=False
        )
    except Exception as e:
        print(f"Error: {str(e)}")