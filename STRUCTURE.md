control-match/
├── .env                                      # Environment variables for API keys and configuration
├── .gitignore                                # Git ignore patterns for Python, env files, etc.
├── requirements.txt                          # Python package dependencies
├── STRUCTURE.md                              # Project structure documentation and file organization (this file)
│
├── scripts/                                  # Command line execution scripts
│   ├── initialize_data.py                    # Orchestrates embedding generation and Pinecone data loading
│   └── analyze_relationships.py              # Runs semantic relationship analysis
│
└── src/
   ├── app.py                                 # Main Flask application and routes
   └── web/                                   # Flask web application
   │   ├── routes.py                          # Web route handlers and blueprints
   │   ├── static/
   │   │   └── js/                            # Frontend JavaScript
   │   │       ├── main.js                    # Main application logic
   │   │       ├── config.js                  # Search configuration management
   │   │       ├── analytics.js               # Search analytics display
   │   │       └── results/                   # Search results rendering
   │   │           ├── base.js                # Base results display functionality
   │   │           └── custom.js              # Custom results display extensions
   │   │
   │   └── templates/                         # Jinja2 HTML templates
   │       ├── index.html                     # Main search interface
   │       ├── config.html                    # Search configuration panel
   │       └── analytics.html                 # Search analytics panel
   │
   └── core/                                  # Core business logic and functionality
       │
       ├── embedder.py                        # Handles text embedding operations
       ├── text_normalizer.py                 # Text normalization and preprocessing
       │
       ├── metadata/                          # Metadata handling and schemas
       │   ├── __init__.py
       │   ├── base.py                        # Base metadata interfaces and abstractions
       │   └── custom.py                      # Custom metadata schema
       │
       ├── connectors/                        # External service clients
       │   ├── __init__.py
       │   ├── base.py                        # Base connector class and error handling
       │   ├── openai.py                      # OpenAI API client for embeddings
       │   ├── cohere.py                      # Cohere API client for reranking
       │   └── pinecone.py                    # Pinecone client for vector storage
       │
       ├── search/                            # Search functionality
       │   ├── __init__.py
       │   ├── manager.py                     # Search operation orchestration and result formatting
       │   ├── response_formatter.py          # Formats search responses and error handling
       │   ├── exceptions.py                  # Search-related exception hierarchy
       │   ├── config/                        # Search configuration management
       │   │   ├── __init__.py
       │   │   ├── config.py                  # Search configuration dataclass and defaults
       │   │   ├── manager.py                 # Configuration loading and saving
       │   │   ├── validator.py               # Configuration validation logic
       │   │   ├── default_config.yaml        # Default search configuration parameters
       │   │   └── saved_config.yaml          # User-saved search configuration
       │   ├── hybridizer.py                  # Combines vector and keyword search
       │   ├── vector_searcher.py             # Vector similarity search operations
       │   ├── keyword_searcher.py            # Keyword matching and text similarity
       │   └── reranker.py                    # Result reranking operations
       │
       └── data_setup/                        # Data initialization tools
           ├── __init__.py
           ├── embeddings_generator.py        # Generates embeddings
           └── data_loader.py                 # Uploads data to Pinecone


System Organization:
- Clear separation between interface (`web/`) and logic (`core/`)
- Main application entry point (`app.py`) at src level
- External dependencies isolated in connectors
- Core business logic centralized and reusable
- Clean execution paths via scripts
- Modular and maintainable structure

Usage Patterns:
- Web interface interacts with core via clean APIs
- Scripts orchestrate core functionality for batch operations
- Core modules can be used independently
- Easy to test and mock dependencies
- Simple to extend or modify functionality

This structure provides a solid foundation for:
- Adding new interfaces
- Extending functionality
- Maintaining clean architecture
- Testable code and validation
- Future development