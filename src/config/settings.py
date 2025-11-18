import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class Settings:
    """
    Configuration management for the translation vector distance system.
    Loads settings from YAML files and environment variables.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize settings.
        
        Args:
            config_path: Path to configuration YAML file. 
                        Defaults to config/experiment_config.yaml
        """
        self._config_path = config_path or self._default_config_path()
        self._config: Dict[str, Any] = {}
        self._load_config()
    
    @staticmethod
    def _default_config_path() -> Path:
        """Get default configuration file path."""
        project_root = Path(__file__).parent.parent.parent
        return project_root / "config" / "experiment_config.yaml"
    
    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        config_path = Path(self._config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {config_path}"
            )
        
        with open(config_path, 'r') as f:
            self._config = yaml.safe_load(f) or {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.
        
        Args:
            key: Configuration key (supports dot notation, e.g., 'agents.cursor')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def get_agent_config(self, agent_type: str) -> Dict[str, Any]:
        """
        Get configuration for specific agent type.
        
        Args:
            agent_type: Agent type ('cursor', 'gemini', 'claude', 'ollama')
            
        Returns:
            Agent configuration dictionary
        """
        return self.get(f'agents.{agent_type}', {})
    
    def get_error_rates(self) -> list:
        """Get list of error rates for experiments."""
        return self.get('experiments.error_rates', [0, 10, 25, 35, 50])
    
    def get_embedding_model(self) -> str:
        """Get embedding model name."""
        return self.get('embeddings.model', 'all-MiniLM-L6-v2')
    
    def get_database_path(self) -> Path:
        """Get database file path."""
        db_path = self.get('database.path', 'data/experiments.db')
        project_root = Path(__file__).parent.parent.parent
        return project_root / db_path
    
    def get_results_dir(self) -> Path:
        """Get results directory path."""
        results_dir = self.get('results.directory', 'results')
        project_root = Path(__file__).parent.parent.parent
        return project_root / results_dir
    
    @property
    def all_config(self) -> Dict[str, Any]:
        """Get all configuration as dictionary."""
        return self._config.copy()


_settings_instance: Optional[Settings] = None


def get_settings(config_path: Optional[str] = None) -> Settings:
    """
    Get singleton settings instance.
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        Settings instance
    """
    global _settings_instance
    
    if _settings_instance is None or config_path is not None:
        _settings_instance = Settings(config_path)
    
    return _settings_instance

