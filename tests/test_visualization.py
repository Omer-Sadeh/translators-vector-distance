import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import tempfile
from pathlib import Path

from src.visualization.dashboard import TranslationDashboard, create_dashboard
from src.visualization.plots import StaticPlots
from src.data.storage import ExperimentStorage


class TestStaticPlots:
    """Tests for StaticPlots class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.tmpdir = tempfile.mkdtemp()
        self.output_dir = Path(self.tmpdir)
        self.plots = StaticPlots(self.output_dir, dpi=100)
        
        # Create sample data
        np.random.seed(42)
        self.data = pd.DataFrame({
            'error_rate_target': np.repeat([0.0, 0.25, 0.5], 10),
            'cosine_distance': np.random.rand(30) * 0.5,
            'euclidean_distance': np.random.rand(30) * 2.0,
            'manhattan_distance': np.random.rand(30) * 3.0,
            'agent_type': np.tile(['cursor', 'gemini', 'claude'], 10),
            'original_text': ['This is a test sentence ' * 3] * 30,
            'word_count': np.random.randint(15, 30, 30),
            'success': [True] * 30
        })
    
    def test_initialization(self):
        """Test plots initialization."""
        assert self.plots.output_dir == self.output_dir
        assert self.plots.dpi == 100
        assert self.output_dir.exists()
    
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    def test_plot_error_rate_vs_distance(self, mock_close, mock_savefig):
        """Test error rate vs distance plot."""
        filepath = self.plots.plot_error_rate_vs_distance(self.data)
        
        assert isinstance(filepath, Path)
        assert 'error_vs_distance' in str(filepath)
        mock_savefig.assert_called_once()
        mock_close.assert_called_once()
    
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    def test_plot_error_rate_with_custom_metric(self, mock_close, mock_savefig):
        """Test plot with custom distance metric."""
        filepath = self.plots.plot_error_rate_vs_distance(
            self.data,
            metric='euclidean_distance',
            save_name='custom'
        )
        
        assert 'custom' in str(filepath)
        mock_savefig.assert_called_once()
    
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    def test_plot_distance_distributions(self, mock_close, mock_savefig):
        """Test distance distribution box plot."""
        filepath = self.plots.plot_distance_distributions(self.data)
        
        assert isinstance(filepath, Path)
        assert 'distance_distributions' in str(filepath)
        mock_savefig.assert_called_once()
    
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    def test_plot_agent_comparison_heatmap(self, mock_close, mock_savefig):
        """Test agent comparison heatmap."""
        filepath = self.plots.plot_agent_comparison_heatmap(self.data)
        
        assert isinstance(filepath, Path)
        assert 'agent_comparison' in str(filepath)
        mock_savefig.assert_called_once()
    
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    def test_plot_sentence_length_effect(self, mock_close, mock_savefig):
        """Test sentence length effect plot."""
        filepath = self.plots.plot_sentence_length_effect(self.data)
        
        assert isinstance(filepath, Path)
        assert 'length_effect' in str(filepath)
        mock_savefig.assert_called_once()
    
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    def test_plot_sentence_length_without_word_count(self, mock_close, mock_savefig):
        """Test length plot creates word_count if missing."""
        data_no_wc = self.data.drop('word_count', axis=1)
        filepath = self.plots.plot_sentence_length_effect(data_no_wc)
        
        assert isinstance(filepath, Path)
        mock_savefig.assert_called_once()
    
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    def test_plot_agent_performance_bars_all_rates(self, mock_close, mock_savefig):
        """Test agent performance bar chart with all error rates."""
        filepath = self.plots.plot_agent_performance_bars(self.data)
        
        assert isinstance(filepath, Path)
        assert 'agent_performance' in str(filepath)
        mock_savefig.assert_called_once()
    
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    def test_plot_agent_performance_bars_specific_rate(self, mock_close, mock_savefig):
        """Test agent performance for specific error rate."""
        filepath = self.plots.plot_agent_performance_bars(
            self.data,
            error_rate=0.25
        )
        
        assert isinstance(filepath, Path)
        mock_savefig.assert_called_once()
    
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    def test_plot_correlation_matrix_default(self, mock_close, mock_savefig):
        """Test correlation matrix with default columns."""
        filepath = self.plots.plot_correlation_matrix(self.data)
        
        assert isinstance(filepath, Path)
        assert 'correlation_matrix' in str(filepath)
        mock_savefig.assert_called_once()
    
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    def test_plot_correlation_matrix_custom_columns(self, mock_close, mock_savefig):
        """Test correlation matrix with custom columns."""
        columns = ['cosine_distance', 'euclidean_distance', 'error_rate_target']
        filepath = self.plots.plot_correlation_matrix(self.data, columns=columns)
        
        assert isinstance(filepath, Path)
        mock_savefig.assert_called_once()
    
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    def test_generate_all_plots(self, mock_close, mock_savefig):
        """Test generating all plots at once."""
        plots = self.plots.generate_all_plots(self.data)
        
        assert isinstance(plots, dict)
        assert 'error_vs_distance' in plots
        assert 'distributions' in plots
        assert 'correlation' in plots
        assert mock_savefig.call_count >= 5
    
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    def test_generate_all_plots_single_agent(self, mock_close, mock_savefig):
        """Test plot generation with single agent."""
        single_agent_data = self.data[self.data['agent_type'] == 'cursor']
        plots = self.plots.generate_all_plots(single_agent_data)
        
        assert isinstance(plots, dict)
        assert 'error_vs_distance' in plots
    
    def test_dpi_setting(self):
        """Test DPI configuration."""
        high_dpi_plots = StaticPlots(self.output_dir, dpi=300)
        assert high_dpi_plots.dpi == 300


class TestTranslationDashboard:
    """Tests for TranslationDashboard class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.tmpdir = tempfile.mkdtemp()
        self.db_path = Path(self.tmpdir) / 'test.db'
        self.storage = ExperimentStorage(self.db_path)
    
    def test_initialization(self):
        """Test dashboard initialization."""
        dashboard = TranslationDashboard(self.storage)
        
        assert dashboard.storage == self.storage
        assert dashboard.host == '127.0.0.1'
        assert dashboard.port == 8050
        assert dashboard.app is not None
    
    def test_initialization_custom_host_port(self):
        """Test dashboard with custom host and port."""
        dashboard = TranslationDashboard(
            self.storage,
            host='0.0.0.0',
            port=9000
        )
        
        assert dashboard.host == '0.0.0.0'
        assert dashboard.port == 9000
    
    def test_load_data_empty(self):
        """Test loading data when database is empty."""
        dashboard = TranslationDashboard(self.storage)
        data = dashboard._load_data()
        
        assert isinstance(data, pd.DataFrame)
        assert data.empty
    
    def test_load_data_with_results(self):
        """Test loading data with experiment results."""
        from src.translation.chain import ChainResult
        from datetime import datetime
        
        # Store test data
        sentence_id = self.storage.store_sentence("Test sentence")
        
        chain_result = ChainResult(
            original_text="Test",
            corrupted_text="Tets",
            error_rate_target=0.25,
            error_rate_actual=0.25,
            translation_fr="Fr",
            translation_he="He",
            translation_en="En",
            agent_type="test",
            total_duration_seconds=10.0,
            individual_durations={'en_to_fr': 3.0, 'fr_to_he': 3.0, 'he_to_en': 4.0},
            success=True,
            error_message=None,
            timestamp=datetime.now(),
            metadata={}
        )
        
        embeddings = {
            'original': np.array([0.1, 0.2, 0.3]),
            'final': np.array([0.2, 0.3, 0.4])
        }
        
        distances = {
            'cosine': 0.1,
            'euclidean': 0.2,
            'manhattan': 0.3
        }
        
        self.storage.store_experiment(sentence_id, chain_result, embeddings, distances)
        
        # Test loading
        dashboard = TranslationDashboard(self.storage)
        data = dashboard._load_data()
        
        assert isinstance(data, pd.DataFrame)
        assert not data.empty
        assert len(data) == 1
    
    def test_setup_layout(self):
        """Test dashboard layout setup."""
        dashboard = TranslationDashboard(self.storage)
        
        assert dashboard.app.layout is not None
    
    def test_setup_callbacks(self):
        """Test callback setup."""
        dashboard = TranslationDashboard(self.storage)
        
        # Callbacks should be registered
        assert hasattr(dashboard.app, 'callback_map')
    
    @patch.object(TranslationDashboard, '_load_data')
    def test_callback_update_agent_options_empty(self, mock_load):
        """Test agent options update with empty data."""
        mock_load.return_value = pd.DataFrame()
        
        dashboard = TranslationDashboard(self.storage)
        
        # Verify callbacks are registered
        assert hasattr(dashboard.app, 'callback_map')
    
    def test_app_title(self):
        """Test dashboard app title."""
        dashboard = TranslationDashboard(self.storage)
        
        assert dashboard.app.title == 'Translation Vector Distance Analysis'


class TestCreateDashboard:
    """Tests for create_dashboard factory function."""
    
    @patch('src.visualization.dashboard.get_settings')
    @patch('src.visualization.dashboard.ExperimentStorage')
    def test_create_dashboard_default(self, mock_storage_class, mock_settings):
        """Test dashboard creation with default settings."""
        mock_settings_instance = MagicMock()
        mock_settings_instance.get_database_path.return_value = Path('/tmp/test.db')
        mock_settings_instance.get.side_effect = lambda key, default: default
        mock_settings.return_value = mock_settings_instance
        
        mock_storage = MagicMock()
        mock_storage_class.return_value = mock_storage
        
        dashboard = create_dashboard()
        
        assert isinstance(dashboard, TranslationDashboard)
        mock_settings.assert_called_once_with(None)
    
    @patch('src.visualization.dashboard.get_settings')
    @patch('src.visualization.dashboard.ExperimentStorage')
    def test_create_dashboard_custom_config(self, mock_storage_class, mock_settings):
        """Test dashboard creation with custom config path."""
        mock_settings_instance = MagicMock()
        mock_settings_instance.get_database_path.return_value = Path('/tmp/test.db')
        mock_settings_instance.get.side_effect = lambda key, default: default
        mock_settings.return_value = mock_settings_instance
        
        mock_storage = MagicMock()
        mock_storage_class.return_value = mock_storage
        
        dashboard = create_dashboard(config_path='/custom/config.yaml')
        
        assert isinstance(dashboard, TranslationDashboard)
        mock_settings.assert_called_once_with('/custom/config.yaml')

