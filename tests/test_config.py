import pytest
import tempfile
from pathlib import Path
import yaml

from src.config.settings import Settings, get_settings


class TestSettings:
    """Tests for Settings configuration management."""
    
    def create_test_config(self, tmpdir):
        """Create a test configuration file."""
        config = {
            'agents': {
                'cursor': {
                    'command': 'cursor-agent',
                    'timeout': 30
                }
            },
            'experiments': {
                'error_rates': [0, 10, 25]
            },
            'embeddings': {
                'model': 'test-model'
            },
            'database': {
                'path': 'test.db'
            }
        }
        
        config_path = Path(tmpdir) / "test_config.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config, f)
        
        return config_path
    
    def test_initialization(self):
        """Test settings initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = self.create_test_config(tmpdir)
            settings = Settings(str(config_path))
            assert settings is not None
    
    def test_get_basic_value(self):
        """Test getting basic configuration value."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = self.create_test_config(tmpdir)
            settings = Settings(str(config_path))
            
            model = settings.get('embeddings.model')
            assert model == 'test-model'
    
    def test_get_with_default(self):
        """Test getting value with default."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = self.create_test_config(tmpdir)
            settings = Settings(str(config_path))
            
            value = settings.get('nonexistent.key', 'default_value')
            assert value == 'default_value'
    
    def test_get_agent_config(self):
        """Test getting agent configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = self.create_test_config(tmpdir)
            settings = Settings(str(config_path))
            
            cursor_config = settings.get_agent_config('cursor')
            assert cursor_config['command'] == 'cursor-agent'
            assert cursor_config['timeout'] == 30
    
    def test_get_error_rates(self):
        """Test getting error rates."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = self.create_test_config(tmpdir)
            settings = Settings(str(config_path))
            
            rates = settings.get_error_rates()
            assert rates == [0, 10, 25]
    
    def test_get_embedding_model(self):
        """Test getting embedding model."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = self.create_test_config(tmpdir)
            settings = Settings(str(config_path))
            
            model = settings.get_embedding_model()
            assert model == 'test-model'
    
    def test_nonexistent_config_file(self):
        """Test with nonexistent config file."""
        with pytest.raises(FileNotFoundError):
            Settings('/nonexistent/path/config.yaml')
    
    def test_singleton_pattern(self):
        """Test singleton pattern for settings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = self.create_test_config(tmpdir)
            
            settings1 = get_settings(str(config_path))
            settings2 = get_settings()
            
            assert settings1 is settings2

