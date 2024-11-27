from pathlib import Path
import yaml
import logging
from typing import Dict, Any, Optional, Union

from .config import SearchConfig
from .validator import validate_config_data

# Configure logging
logger = logging.getLogger(__name__)

class ConfigurationManager:
    """Manages search configuration operations including validation, saving, and loading."""
    
    def __init__(self, config_path: Path = None, default_path: Path = None):
        """Initialize configuration manager with specified paths."""
        # Get the directory where the manager.py file is located
        base_path = Path(__file__).parent
        
        # Set default paths relative to the current file
        self.config_path = config_path or base_path / "saved_config.yaml"
        self.default_path = default_path or base_path / "default_config.yaml"
        self._config: Optional[SearchConfig] = None

    def get_config(self) -> SearchConfig:
        """Get current configuration, initializing with defaults if needed."""
        if self._config is None:
            config_data = self.load_saved_config()
            self._config = SearchConfig(**config_data)
        return self._config

    def load_default_config(self) -> Dict[str, Any]:
        """
        Load default configuration data.
        
        Returns:
            Dict[str, Any]: Default configuration data
            
        Raises:
            IOError: If default configuration cannot be loaded
        """
        try:
            with open(self.default_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading default config: {str(e)}")
            raise IOError(f"Failed to load default configuration: {str(e)}")

    def reset_to_defaults(self) -> Dict[str, Any]:
        """
        Load default configuration without saving it.
        Updates the in-memory configuration but does not affect saved configuration.
        
        Returns:
            Dict[str, Any]: Default configuration data
            
        Raises:
            IOError: If default configuration cannot be loaded
        """
        try:
            # Load default configuration
            default_config = self.load_default_config()
            
            # Update in-memory configuration
            self._config = SearchConfig(**default_config)
            
            return default_config
            
        except Exception as e:
            logger.error(f"Error resetting to defaults: {str(e)}")
            raise IOError(f"Failed to reset configuration: {str(e)}")

    def format_config_response(self, config: Union[SearchConfig, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Format configuration for API response.
        
        Args:
            config: SearchConfig instance or config dictionary
            
        Returns:
            Dict[str, Any]: Formatted configuration response
        """
        # Convert to dict if SearchConfig instance
        config_dict = config.__dict__ if isinstance(config, SearchConfig) else config
        
        return {
            'scoring_weights': {
                'vector_weight': config_dict['vector_weight'],
                'keyword_weight': config_dict['keyword_weight']
            },
            'thresholds': {
                'min_vector_score': config_dict['min_vector_score'],
                'min_keyword_score': config_dict['min_keyword_score'],
                'min_combined_score': config_dict['min_combined_score'],
                'exact_match_min_vector_score': config_dict['exact_match_min_vector_score'],
                'exact_match_min_keyword_score': config_dict['exact_match_min_keyword_score']
            },
            'reranking': {
                'enable_reranking': config_dict['enable_reranking']
            }
        }

    def load_saved_config(self) -> Dict[str, Any]:
        """
        Load configuration data from file, falling back to defaults if needed.
        
        Returns:
            Dict[str, Any]: Configuration data
            
        Raises:
            IOError: If configuration cannot be loaded
        """
        try:
            # Try to load saved config first
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config_data = yaml.safe_load(f)
                # Validate saved config before using it
                validate_config_data(config_data)
                return config_data
            
            # Fall back to default config
            logger.info("No saved config found, using defaults")
            with open(self.default_path, 'r') as f:
                return yaml.safe_load(f)
                
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            # If there's any error with saved config, fall back to defaults
            try:
                with open(self.default_path, 'r') as f:
                    return yaml.safe_load(f)
            except Exception as default_error:
                raise IOError(f"Failed to load configuration: {str(default_error)}")

    def save_config(self, config_data: Dict[str, Any]) -> None:
        """
        Save configuration to file and update current config.
        
        Args:
            config_data: Configuration dictionary to save
            
        Raises:
            ValueError: If configuration is invalid
            IOError: If there's an error saving the configuration
        """
        try:
            # Get current config to fill in any missing fields
            current_config = self.load_saved_config()
            
            # Update with new values
            current_config.update(config_data)
            
            # Validate complete configuration
            validate_config_data(current_config)
            
            # Convert reranking flag to boolean
            if 'enable_reranking' in current_config:
                current_config['enable_reranking'] = bool(current_config['enable_reranking'])
                
            # Create parent directory if it doesn't exist
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save configuration
            with open(self.config_path, 'w') as f:
                yaml.safe_dump(current_config, f, sort_keys=False)
            
            # Update current config
            self._config = SearchConfig(**current_config)
                
        except Exception as e:
            logger.error(f"Error saving config: {str(e)}")
            raise IOError(f"Failed to save configuration: {str(e)}")

    def update_config(self, config_data: Dict[str, Any]) -> SearchConfig:
        """
        Process, validate, and apply configuration update.
        
        Args:
            config_data: New configuration values
            
        Returns:
            SearchConfig: Updated configuration instance
            
        Raises:
            ValueError: If configuration is invalid
        """
        processed_data = self.process_config_update(config_data)
        self._config = SearchConfig(**processed_data)
        return self._config

    def process_config_update(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and validate configuration update.
        
        Args:
            config_data: New configuration values
            
        Returns:
            Dict: Processed configuration data
            
        Raises:
            ValueError: If configuration is invalid
        """
        if not config_data:
            raise ValueError("No configuration data provided")
        
        # Get current config as base
        current_config = self.load_saved_config()
        
        # Process and validate new values
        for key, value in config_data.items():
            if key not in current_config:
                raise ValueError(f"Invalid configuration key: {key}")
                
            if 'score' in key or 'weight' in key:
                try:
                    value = float(value)
                    if not 0 <= value <= 1:
                        raise ValueError(
                            f"Invalid threshold value for {key}. Must be between 0 and 1."
                        )
                except (ValueError, TypeError):
                    raise ValueError(f"Invalid value for {key}. Must be a number.")
            
            current_config[key] = value
        
        # Handle reranking flag
        if 'enable_reranking' in current_config:
            current_config['enable_reranking'] = bool(current_config['enable_reranking'])
        
        return current_config