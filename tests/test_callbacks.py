import pytest
from unittest.mock import Mock, MagicMock, patch
import pandas as pd
import numpy as np
from dash import Dash

from src.visualization.callbacks_filters import register_filter_callbacks, filter_data
from src.visualization.callbacks_stats import register_stats_callbacks
from src.visualization.callbacks_plots import register_plot_callbacks
from src.visualization.dashboard_callbacks import register_callbacks


class TestFilterCallbacks:
    """Tests for filter callbacks."""
    
    def test_register_filter_callbacks(self):
        """Test registering filter callbacks."""
        app = Mock(spec=Dash)
        dashboard = Mock()
        dashboard._load_data = Mock(return_value=pd.DataFrame({
            'agent_type': ['cursor', 'gemini', 'cursor']
        }))
        
        register_filter_callbacks(app, dashboard)
        
        app.callback.assert_called()
    
    def test_filter_data_no_filters(self):
        """Test filter_data with no filters applied."""
        data = pd.DataFrame({
            'agent_type': ['cursor', 'gemini', 'claude'],
            'error_rate_target': [0.0, 0.1, 0.25]
        })
        
        result = filter_data(data, None, [0, 50])
        
        assert len(result) == 3
        assert 'agent_type' in result.columns
    
    def test_filter_data_with_agent_filter(self):
        """Test filter_data with agent filter."""
        data = pd.DataFrame({
            'agent_type': ['cursor', 'gemini', 'claude', 'cursor'],
            'error_rate_target': [0.0, 0.1, 0.25, 0.5]
        })
        
        result = filter_data(data, ['cursor'], [0, 50])
        
        assert len(result) == 2
        assert all(result['agent_type'] == 'cursor')
    
    def test_filter_data_with_error_rate_filter(self):
        """Test filter_data with error rate filter."""
        data = pd.DataFrame({
            'agent_type': ['cursor', 'gemini', 'claude'],
            'error_rate_target': [0.0, 0.1, 0.5]
        })
        
        result = filter_data(data, None, [0, 25])
        
        assert len(result) == 2
        assert all(result['error_rate_target'] <= 0.25)
    
    def test_filter_data_both_filters(self):
        """Test filter_data with both filters."""
        data = pd.DataFrame({
            'agent_type': ['cursor', 'gemini', 'cursor', 'cursor'],
            'error_rate_target': [0.0, 0.1, 0.25, 0.5]
        })
        
        result = filter_data(data, ['cursor'], [0, 30])
        
        assert len(result) == 2
        assert all(result['agent_type'] == 'cursor')
        assert all(result['error_rate_target'] <= 0.30)


class TestStatsCallbacks:
    """Tests for stats callbacks."""
    
    def test_register_stats_callbacks(self):
        """Test registering stats callbacks."""
        app = Mock(spec=Dash)
        dashboard = Mock()
        
        register_stats_callbacks(app, dashboard)
        
        app.callback.assert_called()


class TestPlotCallbacks:
    """Tests for plot callbacks."""
    
    def test_register_plot_callbacks(self):
        """Test registering plot callbacks."""
        app = Mock(spec=Dash)
        dashboard = Mock()
        
        register_plot_callbacks(app, dashboard)
        
        assert app.callback.call_count >= 4


class TestDashboardCallbacks:
    """Tests for main dashboard callbacks."""
    
    def test_register_all_callbacks(self):
        """Test registering all callbacks."""
        app = Mock(spec=Dash)
        dashboard = Mock()
        
        register_callbacks(app, dashboard)
        
        assert app.callback.call_count >= 6

