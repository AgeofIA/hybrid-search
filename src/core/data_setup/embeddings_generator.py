import os
from pathlib import Path
import json
import pandas as pd
from tqdm.auto import tqdm
from dotenv import load_dotenv

from embedder import create_batch_embeddings
from metadata import metadata_schema

# Load environment variables
load_dotenv()

# Constants
BATCH_SIZE = 32
EMBEDDINGS_COLUMN = 'embedding_vector'
NORMALIZED_TEXT_COLUMN = 'normalized_statement'

def get_embeddings_path(csv_path: str) -> Path:
    """Get the expected path for embeddings CSV."""
    input_path = Path(csv_path)
    return input_path.parent / f"{input_path.stem}_embeddings{input_path.suffix}"

def get_text_content(row: pd.Series) -> str:
    """
    Extract text content for embedding using custom metadata schema.
    
    Args:
        row: DataFrame row containing data
        
    Returns:
        str: Text content for embedding
    """
    metadata = metadata_schema.process(row.to_dict())
    return metadata.normalized_text

def generate_embeddings(csv_path: str) -> str:
    """
    Generate embeddings for text content if needed.
    If embeddings file exists, returns its path without regenerating.
    
    Args:
        csv_path: Path to source CSV file
        
    Returns:
        str: Path to CSV file with embeddings
    """
    embeddings_path = get_embeddings_path(csv_path)
    
    # Check if embeddings file already exists
    if embeddings_path.exists():
        print(f"Found existing embeddings file: {embeddings_path}")
        return str(embeddings_path)
    
    print("No existing embeddings found. Generating new embeddings...")
    print("Loading source CSV data...")
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} rows")
    
    # Initialize new columns
    df[EMBEDDINGS_COLUMN] = None
    df[NORMALIZED_TEXT_COLUMN] = None
    
    failed_rows = []
    
    # Process in batches
    for i in tqdm(range(0, len(df), BATCH_SIZE)):
        batch_df = df.iloc[i:i + BATCH_SIZE]
        try:
            # Extract texts using schema
            texts = [get_text_content(row) for _, row in batch_df.iterrows()]
            
            # Store normalized texts
            for idx, text in zip(batch_df.index, texts):
                df.at[idx, NORMALIZED_TEXT_COLUMN] = text
            
            # Generate embeddings
            batch_embeddings = create_batch_embeddings(texts)
            
            # Store embeddings
            for idx, embedding in zip(batch_df.index, batch_embeddings):
                df.at[idx, EMBEDDINGS_COLUMN] = json.dumps(embedding)
                
        except Exception as e:
            print(f"\nError processing batch at index {i}: {str(e)}")
            failed_rows.extend(batch_df.index.tolist())
            continue
    
    # Save results to new file
    print(f"\nSaving embeddings to new CSV: {embeddings_path}")
    df.to_csv(embeddings_path, index=False)
    
    print(f"\nProcessing complete!")
    print(f"Successfully processed: {len(df) - len(failed_rows)} rows")
    if failed_rows:
        print(f"Failed to process: {len(failed_rows)} rows")
        
    return str(embeddings_path)

if __name__ == "__main__":
    try:
        csv_path = os.getenv('DATA_CSV_PATH')
        if not csv_path:
            raise ValueError("DATA_CSV_PATH not found in environment variables")
            
        output_path = generate_embeddings(csv_path)
        print(f"\nEmbeddings file path: {output_path}")
        
    except Exception as e:
        print(f"Error: {str(e)}")