import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pathlib import Path
from typing import Dict

from src.visualization.plot_types import (
    plot_error_rate_vs_distance,
    plot_distance_distributions,
    plot_agent_comparison_heatmap,
    plot_sentence_length_effect,
    plot_agent_performance_bars,
    plot_correlation_matrix
)

sns.set_style('whitegrid')
sns.set_palette('husl')


class StaticPlots:
    """
    Publication-quality static visualizations (300 DPI).
    
    Generates high-resolution graphs for research papers and reports.
    """
    
    def __init__(self, output_dir: Path, dpi: int = 300):
        """
        Initialize plot generator.
        
        Args:
            output_dir: Directory to save figures
            dpi: Resolution in dots per inch
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.dpi = dpi
    
    def plot_error_rate_vs_distance(
        self,
        data: pd.DataFrame,
        metric: str = 'cosine_distance',
        save_name: str = 'error_vs_distance'
    ) -> Path:
        """Line plot: Error rate vs vector distance with confidence intervals."""
        return plot_error_rate_vs_distance(
            self.output_dir, self.dpi, data, metric, save_name
        )
    
    def plot_distance_distributions(
        self,
        data: pd.DataFrame,
        metric: str = 'cosine_distance',
        save_name: str = 'distance_distributions'
    ) -> Path:
        """Box plot: Distribution of distances per error rate."""
        return plot_distance_distributions(
            self.output_dir, self.dpi, data, metric, save_name
        )
    
    def plot_agent_comparison_heatmap(
        self,
        data: pd.DataFrame,
        metric: str = 'cosine_distance',
        save_name: str = 'agent_comparison'
    ) -> Path:
        """Heatmap: Agent comparison across error rates."""
        return plot_agent_comparison_heatmap(
            self.output_dir, self.dpi, data, metric, save_name
        )
    
    def plot_sentence_length_effect(
        self,
        data: pd.DataFrame,
        metric: str = 'cosine_distance',
        save_name: str = 'length_effect'
    ) -> Path:
        """Scatter plot: Sentence length vs distance, colored by error rate."""
        return plot_sentence_length_effect(
            self.output_dir, self.dpi, data, metric, save_name
        )
    
    def plot_agent_performance_bars(
        self,
        data: pd.DataFrame,
        metric: str = 'cosine_distance',
        error_rate: float = None,
        save_name: str = 'agent_performance'
    ) -> Path:
        """Bar chart: Performance comparison across agents."""
        return plot_agent_performance_bars(
            self.output_dir, self.dpi, data, metric, error_rate, save_name
        )
    
    def plot_correlation_matrix(
        self,
        data: pd.DataFrame,
        columns: list = None,
        save_name: str = 'correlation_matrix'
    ) -> Path:
        """Correlation matrix heatmap."""
        return plot_correlation_matrix(
            self.output_dir, self.dpi, data, columns, save_name
        )
    
    def generate_all_plots(self, data: pd.DataFrame) -> Dict[str, Path]:
        """
        Generate all standard plots.
        
        Args:
            data: DataFrame with experimental results
            
        Returns:
            Dictionary mapping plot names to file paths
        """
        plots = {}
        
        try:
            plots['error_vs_distance'] = self.plot_error_rate_vs_distance(data)
            plots['distributions'] = self.plot_distance_distributions(data)
            
            if 'agent_type' in data.columns and data['agent_type'].nunique() > 1:
                plots['agent_comparison'] = self.plot_agent_comparison_heatmap(data)
                plots['agent_performance'] = self.plot_agent_performance_bars(data)
            
            plots['length_effect'] = self.plot_sentence_length_effect(data)
            plots['correlation'] = self.plot_correlation_matrix(data)
            
        except Exception as e:
            print(f"Error generating plots: {e}")
        
        return plots
