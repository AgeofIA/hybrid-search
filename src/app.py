"""
Search Application Server

Main entry point for the search application. Initializes and configures
the complete search infrastructure.

Components:
    - Flask web application: Handles HTTP requests and routing
    - Search components: Provides hybrid search functionality
    - Configuration: Manages application settings
    - Logging: Structured logging for monitoring and debugging

Required Environment Variables:
    All configuration is loaded from .env file:
    - SEARCH_API_KEY: API key for search service
    - SEARCH_ENDPOINT: Search service endpoint
    See .env.example for complete list.

Usage:
    $ python app.py
    
    Application will start on http://localhost:5001
"""

import sys
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from loguru import logger

# Add core directory to Python path
core_path = str(Path(__file__).parent / 'core')
if core_path not in sys.path:
    sys.path.insert(0, core_path)

from search.config.manager import ConfigurationManager
from search.hybridizer import hybrid_search
from search.manager import SearchManager
from web.routes import search_bp, init_routes


class AppError(Exception):
    """Base exception for application-level errors."""
    pass


def create_app() -> Flask:
    """
    Initialize and configure the Flask application.
    
    Returns:
        Flask: Configured Flask application instance
    
    Raises:
        AppError: If initialization fails
    """
    try:
        # Load environment variables
        load_dotenv()
        
        # Initialize logging
        _init_logging()
        logger.info("Starting application initialization")
        
        # Initialize Flask app
        app = Flask(__name__,
                   template_folder='web/templates',
                   static_folder='web/static',
                   static_url_path='/static')
        
        # Initialize components
        logger.info("Initializing components")
        config_manager = ConfigurationManager()
        search_manager = SearchManager(hybrid_search, config_manager)
        
        # Initialize routes
        logger.info("Setting up routes")
        init_routes(search_manager, config_manager, hybrid_search)
        app.register_blueprint(search_bp)
        
        logger.success("Application initialized successfully")
        return app
        
    except Exception as e:
        logger.error("Application initialization failed", error=str(e))
        raise AppError(f"Initialization failed: {str(e)}")

def _init_logging():
    """Configure structured logging for the application."""
    logger.remove()  # Remove default handler
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
        colorize=True,
        serialize=False  # Disable JSON serialization
    )


# Initialize application
try:
    app = create_app()
except AppError as e:
    logger.critical("Failed to start application", error=str(e))
    sys.exit(1)


if __name__ == "__main__":
    app.run(debug=True, port=5001)