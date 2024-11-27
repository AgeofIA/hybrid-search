import os
import sys
from dotenv import load_dotenv

# Add src directory to Python path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'core'))
sys.path.append(src_path)

# Now we can import from core directly
from data_setup.embeddings_generator import generate_embeddings
from data_setup.data_loader import upload_to_pinecone

# Load environment variables
load_dotenv()

def check_environment():
    """Check for required environment variables."""
    required_vars = [
        'OPENAI_API_KEY',
        'PINECONE_API_KEY',
        'PINECONE_INDEX_NAME',
        'DATA_CSV_PATH'
    ]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        print("Missing required environment variables:", missing)
        return False
    return True

def setup_index(recreate_index: bool = True):
    """Set up search index."""
    if not check_environment():
        return
    
    csv_path = os.getenv('DATA_CSV_PATH')
    
    print("Step 1: Checking/Generating embeddings...")
    embeddings_csv = generate_embeddings(csv_path)
    
    print("\nStep 2: Uploading to Pinecone...")
    upload_to_pinecone(embeddings_csv, recreate_index)
    
    print("\nIndex setup complete!")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--recreate-index', action='store_true',
                       help="Recreate Pinecone index before uploading")
    
    args = parser.parse_args()
    
    try:
        setup_index(recreate_index=args.recreate_index)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)