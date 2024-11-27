# Hybrid Semantic Search Platform

A flexible full-stack platform for hybrid semantic search combining vector similarity and keyword matching, with support for custom metadata schemas.

## 🌟 Features

- **Hybrid Search Algorithm**
  - Vector similarity using OpenAI embeddings
  - Keyword matching with BM25 ranking
  - Configurable weight distribution
  - Semantic reranking via Cohere

- **Interactive Web Interface**
  - Real-time search configuration
  - Detailed analytics dashboard
  - Dynamic result visualization
  - Configurable result display

- **Robust Backend**
  - Flask-based REST API
  - Modular connector architecture
  - Structured error handling
  - Comprehensive logging

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Pinecone account
- OpenAI API key
- Cohere API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/hybrid-search.git
cd hybrid-search
```

2. Create and activate a conda environment:
```bash
conda env create -f config/environment.yaml
conda activate semantic
```

3. Set up environment variables:
```bash
cp .env.example .env
```

Edit `.env` with your API keys:
```
OPENAI_API_KEY=your_openai_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX_NAME=your_index_name
DATA_CSV_PATH=path/to/your/data.csv
```

### Running the Application

Start the Flask server:
```bash
python src/app.py
```

## 🚧 Work in Progress

This project is actively being developed with a focus on making metadata schemas more pluggable and extensible. Future updates will include:

- Schema discovery and auto-registration
- Additional metadata validators
- Enhanced schema documentation
- More example implementations
- Schema migration tools

## 🙏 Third-Party Services

This project relies on the following third-party services:

- **OpenAI** - Text embedding generation
- **Cohere** - Semantic reranking
- **Pinecone** - Vector database and similarity search
- **Flask** - Web framework
- **Tailwind CSS** - UI styling

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.