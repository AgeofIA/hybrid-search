import csv
import pandas as pd
from tqdm.auto import tqdm
import time
import os
import sys
from typing import Dict, Set, Optional
from dotenv import load_dotenv

# Add src directory to Python path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'core'))
sys.path.append(src_path)

# Now we can import from core directly
from search.hybridizer import hybrid_search
from embedder import create_embedding
from search.config.manager import ConfigurationManager
from metadata import metadata_schema

load_dotenv()

class AnalysisStats:
    """Track statistics for semantic analysis."""
    def __init__(self):
        self.total_processed: int = 0
        self.total_matches: int = 0
        self.entries_with_matches: int = 0
        self.category_match_counts: Dict[str, int] = {}
        self.category_pairs: Set[tuple] = set()
    
    def update_category_stats(self, source_category: str, target_category: str) -> None:
        """Update category-based statistics."""
        category_key = f"{source_category}->{target_category}"
        self.category_match_counts[category_key] = \
            self.category_match_counts.get(category_key, 0) + 1
        self.category_pairs.add(tuple(sorted([source_category, target_category])))

    def print_summary(self) -> None:
        """Print comprehensive analysis statistics."""
        print("\nAnalysis complete!")
        print(f"\nSummary Statistics:")
        print(f"Total entries processed: {self.total_processed}")
        print(f"Entries with matches: {self.entries_with_matches} " +
              f"({(self.entries_with_matches/self.total_processed*100):.1f}%)")
        print(f"Total matches written: {self.total_matches}")
        print(f"Average matches per entry: {(self.total_matches/self.total_processed):.1f}")

        print("\nCategory Pair Statistics:")
        for pair in sorted(self.category_pairs):
            print(f"{pair[0]} <-> {pair[1]}")
            
        print("\nDirectional Match Counts:")
        for category_pair, count in sorted(self.category_match_counts.items()):
            print(f"{category_pair}: {count} matches")

def analyze_semantic_relationships(
    csv_path: str,
    output_path: str,
    metadata_schema,
    category_field: str,
    id_field: str,
    max_entries: Optional[int] = None,
    requests_per_minute: int = 10
) -> None:
    """
    Analyze semantic relationships between entries using hybrid search.
    Only includes matches between different categories using configured thresholds.
    
    Args:
        csv_path: Path to source CSV file
        output_path: Path to save results CSV
        metadata_schema: Schema for processing metadata
        category_field: Field name used for categorization/grouping
        id_field: Field name for unique identifier
        max_entries: Maximum number of entries to process (None for all)
        requests_per_minute: Maximum API requests per minute
    """
    # Initialize configuration
    config_manager = ConfigurationManager()
    search_config = config_manager.get_config()
    delay_between_requests = 60.0 / requests_per_minute
    last_request_time = 0

    # Load source data
    print("Loading source data...")
    df = pd.read_csv(csv_path)
    if max_entries:
        df = df.head(max_entries)
        print(f"Limited to first {max_entries} entries for testing")

    # Initialize stats tracking
    stats = AnalysisStats()

    # Initialize CSV output
    print("\nAnalyzing semantic relationships...")
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header based on metadata schema fields
        writer.writerow(metadata_schema.get_csv_header_fields())

        # Process each entry
        for idx, row in tqdm(df.iterrows(), total=len(df)):
            try:
                # Apply rate limiting
                time_since_last_request = time.time() - last_request_time
                if time_since_last_request < delay_between_requests:
                    time.sleep(delay_between_requests - time_since_last_request)

                # Process source data through schema
                source_metadata = metadata_schema.process(row.to_dict())
                
                # Create embedding and tokens for search
                query_embedding = create_embedding(source_metadata.text)
                query_tokens = source_metadata.normalized_text.split()
                
                # Record API request time
                last_request_time = time.time()

                # Perform hybrid search
                results = hybrid_search(
                    query_vector=query_embedding,
                    query_tokens=query_tokens,
                    config=search_config
                )

                # Update statistics
                stats.total_processed += 1
                has_matches = False

                # Get matches from results
                matches = results.get('matches', [])
                if not matches:
                    continue

                # Process and write matches
                for match in matches:
                    try:
                        # Process target metadata through schema
                        target_metadata = metadata_schema.process(match['metadata'])
                        
                        # Skip self-matches and same category matches
                        source_category = getattr(source_metadata, category_field)
                        target_category = getattr(target_metadata, category_field)
                        source_id = getattr(source_metadata, id_field)
                        target_id = getattr(target_metadata, id_field)
                        
                        if source_id == target_id or source_category == target_category:
                            continue

                        # Update category statistics
                        stats.update_category_stats(source_category, target_category)

                        # Write match data
                        writer.writerow(
                            metadata_schema.format_csv_row(
                                source_metadata, 
                                target_metadata,
                                match.get('rank', 0),
                                match['scores']
                            )
                        )
                        
                        has_matches = True
                        stats.total_matches += 1

                    except Exception as e:
                        print(f"\nError processing match: {str(e)}")
                        continue

                if has_matches:
                    stats.entries_with_matches += 1
                    
            except Exception as e:
                print(f"\nError processing entry {getattr(source_metadata, id_field, 'unknown')}: {str(e)}")
                continue

    # Print final statistics
    stats.print_summary()


if __name__ == "__main__":
    analyze_semantic_relationships(
        csv_path=os.environ.get('DATA_CSV_PATH'),
        output_path="matches/semantic_matches.csv",
        metadata_schema=metadata_schema,
        category_field=metadata_schema.group_by_field,
        id_field=metadata_schema.id_field,
        max_entries=10,  # Set to None to process all entries
        requests_per_minute=10
    )