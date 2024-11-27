from flask import Blueprint, render_template, request, jsonify
import logging
from metadata import metadata_schema

logger = logging.getLogger(__name__)

# Create blueprint
search_bp = Blueprint('search', __name__)

# Store managers as None initially
_search_manager = None
_config_manager = None
_search_client = None

def init_routes(search_manager, config_manager, search_client):
    """Initialize route dependencies."""
    global _search_manager, _config_manager, _search_client
    _search_manager = search_manager
    _config_manager = config_manager
    _search_client = search_client

@search_bp.route('/')
def home():
    """Render the search interface."""
    return render_template('home.html')

@search_bp.route('/search', methods=['POST'])
def search():
    """Handle search request."""
    response, status_code = _search_manager.execute_search(request.json)
    return jsonify(response), status_code

# Configuration Retrieval Routes
@search_bp.route('/search/config', methods=['GET'])
def get_search_config():
    """Get current search configuration and thresholds."""
    try:
        current_config = _config_manager.get_config()
        return jsonify(_config_manager.format_config_response(current_config))
    except Exception as e:
        logger.error(f"Config retrieval error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve configuration'}), 500

@search_bp.route('/search/default-config', methods=['GET'])
def get_default_config():
    """Get factory default configuration."""
    try:
        default_config = _config_manager.load_default_config()
        return jsonify(_config_manager.format_config_response(default_config))
    except Exception as e:
        logger.error(f"Error loading default config: {str(e)}")
        return jsonify({'error': 'Failed to load default configuration'}), 500

@search_bp.route('/search/saved-config', methods=['GET'])
def get_saved_config():
    """Get user's saved configuration if it exists."""
    try:
        saved_config = _config_manager.load_saved_config()
        if not saved_config:
            return jsonify({'error': 'No saved configuration found'}), 404
        return jsonify(saved_config)
    except IOError as e:
        logger.error(f"Error loading saved config: {str(e)}")
        return jsonify({'error': 'Failed to load saved configuration'}), 500

# Configuration Modification Routes
@search_bp.route('/search/config', methods=['POST'])
def update_search_config():
    """Update search configuration and thresholds."""
    try:
        new_config = request.json
        updated_config = _config_manager.update_config(new_config)
        _search_client.config = updated_config
        return jsonify({
            'status': 'success',
            'config': _config_manager.format_config_response(updated_config)
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Config update error: {str(e)}")
        return jsonify({
            'error': 'Failed to update configuration',
            'details': str(e)
        }), 400

@search_bp.route('/search/saved-config', methods=['POST'])
def save_config():
    """Save user's configuration preferences."""
    try:
        new_config = request.json
        _config_manager.save_config(new_config)
        return jsonify({
            'status': 'success',
            'message': 'Configuration saved successfully'
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except IOError as e:
        logger.error(f"Error saving config: {str(e)}")
        return jsonify({
            'error': 'Failed to save configuration',
            'details': str(e)
        }), 500

@search_bp.route('/search/reset-config', methods=['POST'])
def reset_config():
    """Reset to factory defaults without affecting saved configuration."""
    try:
        # Get default configuration and update in-memory state
        default_config = _config_manager.reset_to_defaults()
        
        # Update search client with default configuration
        _search_client.config = _config_manager.get_config()
        
        return jsonify({
            'status': 'success',
            'config': _config_manager.format_config_response(default_config),
            'message': 'Configuration reset to defaults (not saved)'
        })
    except Exception as e:
        logger.error(f"Error resetting config: {str(e)}")
        return jsonify({
            'error': 'Failed to reset configuration',
            'details': str(e)
        }), 500

@search_bp.route('/metadata/schema/frontend-config', methods=['GET'])
def get_schema_frontend_config():
    """Get frontend display configuration for metadata schema."""
    try:
        return jsonify(metadata_schema.get_frontend_config())
    except Exception as e:
        logger.error(f"Error retrieving schema config: {str(e)}")
        return jsonify({'error': 'Failed to retrieve schema configuration'}), 500