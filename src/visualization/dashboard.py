import dash
import pandas as pd
from typing import Optional
from pathlib import Path

from src.data.storage import ExperimentStorage
from src.config import get_settings
from src.visualization.dashboard_components import create_layout
from src.visualization.dashboard_callbacks import register_callbacks


class TranslationDashboard:
    """
    Interactive Plotly Dash dashboard for experiment visualization.
    
    Provides real-time exploration of translation quality experiments
    with interactive controls and multiple visualization types.
    """
    
    def __init__(
        self,
        storage: ExperimentStorage,
        host: str = '127.0.0.1',
        port: int = 8050
    ):
        """
        Initialize dashboard.
        
        Args:
            storage: ExperimentStorage instance
            host: Dashboard host
            port: Dashboard port
        """
        self.storage = storage
        self.host = host
        self.port = port
        
        self.app = dash.Dash(
            __name__,
            title='Translation Vector Distance Analysis'
        )
        
        self._setup_layout()
        self._setup_callbacks()
    
    def _load_data(self) -> pd.DataFrame:
        """
        Load data from storage.
        
        Returns:
            DataFrame with experiment results
        """
        results = self.storage.get_all_results()
        if not results:
            return pd.DataFrame()
        return pd.DataFrame(results)
    
    def _setup_layout(self):
        """Setup dashboard layout using components module."""
        self.app.layout = create_layout()
    
    def _setup_callbacks(self):
        """Setup dashboard callbacks using callbacks module."""
        register_callbacks(self.app, self)
    
    def run(self, debug: bool = False):
        """
        Run the dashboard server.
        
        Args:
            debug: Enable debug mode
        """
        self.app.run(host=self.host, port=self.port, debug=debug)


def create_dashboard(config_path: Optional[str] = None) -> TranslationDashboard:
    """
    Create dashboard instance from configuration.
    
    Args:
        config_path: Optional configuration file path
        
    Returns:
        TranslationDashboard instance
    """
    settings = get_settings(config_path)
    storage = ExperimentStorage(settings.get_database_path())
    
    host = settings.get('dashboard.host', '127.0.0.1')
    port = settings.get('dashboard.port', 8050)
    
    return TranslationDashboard(storage, host, port)
