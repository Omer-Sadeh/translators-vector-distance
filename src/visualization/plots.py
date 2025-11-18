import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Optional, Dict
from scipy import stats

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
        """
        Line plot: Error rate vs vector distance with confidence intervals.
        
        Args:
            data: DataFrame with 'error_rate_target' and distance columns
            metric: Distance metric column name
            save_name: Filename (without extension)
            
        Returns:
            Path to saved figure
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        grouped = data.groupby('error_rate_target')[metric].agg(['mean', 'std', 'count'])
        error_rates = grouped.index * 100
        means = grouped['mean']
        stds = grouped['std']
        counts = grouped['count']
        
        ci = 1.96 * stds / np.sqrt(counts)
        
        ax.plot(error_rates, means, 'o-', linewidth=2, markersize=8, label='Mean')
        ax.fill_between(error_rates, means - ci, means + ci, alpha=0.3, label='95% CI')
        
        ax.set_xlabel('Spelling Error Rate (%)', fontsize=14)
        ax.set_ylabel(f'{metric.replace("_", " ").title()}', fontsize=14)
        ax.set_title('Translation Quality Degradation vs Input Error Rate', fontsize=16, pad=20)
        ax.legend(fontsize=12)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        filepath = self.output_dir / f'{save_name}.png'
        plt.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def plot_distance_distributions(
        self,
        data: pd.DataFrame,
        metric: str = 'cosine_distance',
        save_name: str = 'distance_distributions'
    ) -> Path:
        """
        Box plot: Distribution of distances per error rate.
        
        Args:
            data: DataFrame with data
            metric: Distance metric column
            save_name: Filename
            
        Returns:
            Path to saved figure
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        data_plot = data.copy()
        data_plot['error_rate_pct'] = data_plot['error_rate_target'] * 100
        
        sns.boxplot(
            data=data_plot,
            x='error_rate_pct',
            y=metric,
            ax=ax,
            palette='Set2'
        )
        
        ax.set_xlabel('Spelling Error Rate (%)', fontsize=14)
        ax.set_ylabel(f'{metric.replace("_", " ").title()}', fontsize=14)
        ax.set_title('Distribution of Vector Distances by Error Rate', fontsize=16, pad=20)
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        filepath = self.output_dir / f'{save_name}.png'
        plt.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def plot_agent_comparison_heatmap(
        self,
        data: pd.DataFrame,
        metric: str = 'cosine_distance',
        save_name: str = 'agent_comparison'
    ) -> Path:
        """
        Heatmap: Agent comparison across error rates.
        
        Args:
            data: DataFrame with data
            metric: Distance metric
            save_name: Filename
            
        Returns:
            Path to saved figure
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        pivot = data.pivot_table(
            values=metric,
            index='agent_type',
            columns='error_rate_target',
            aggfunc='mean'
        )
        
        pivot.columns = [f'{int(c*100)}%' for c in pivot.columns]
        
        sns.heatmap(
            pivot,
            annot=True,
            fmt='.4f',
            cmap='YlOrRd',
            ax=ax,
            cbar_kws={'label': metric.replace('_', ' ').title()}
        )
        
        ax.set_xlabel('Error Rate', fontsize=14)
        ax.set_ylabel('Agent Type', fontsize=14)
        ax.set_title('Agent Performance Comparison Across Error Rates', fontsize=16, pad=20)
        
        plt.tight_layout()
        filepath = self.output_dir / f'{save_name}.png'
        plt.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def plot_sentence_length_effect(
        self,
        data: pd.DataFrame,
        metric: str = 'cosine_distance',
        save_name: str = 'length_effect'
    ) -> Path:
        """
        Scatter plot: Sentence length vs distance, colored by error rate.
        
        Args:
            data: DataFrame with data
            metric: Distance metric
            save_name: Filename
            
        Returns:
            Path to saved figure
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if 'word_count' not in data.columns:
            data['word_count'] = data['original_text'].str.split().str.len()
        
        scatter = ax.scatter(
            data['word_count'],
            data[metric],
            c=data['error_rate_target'] * 100,
            cmap='viridis',
            alpha=0.6,
            s=100,
            edgecolors='black',
            linewidth=0.5
        )
        
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Error Rate (%)', fontsize=12)
        
        ax.set_xlabel('Sentence Length (words)', fontsize=14)
        ax.set_ylabel(f'{metric.replace("_", " ").title()}', fontsize=14)
        ax.set_title('Effect of Sentence Length on Translation Quality', fontsize=16, pad=20)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        filepath = self.output_dir / f'{save_name}.png'
        plt.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def plot_agent_performance_bars(
        self,
        data: pd.DataFrame,
        metric: str = 'cosine_distance',
        error_rate: Optional[float] = None,
        save_name: str = 'agent_performance'
    ) -> Path:
        """
        Bar chart: Performance comparison across agents.
        
        Args:
            data: DataFrame with data
            metric: Distance metric
            error_rate: Specific error rate to filter (None for all)
            save_name: Filename
            
        Returns:
            Path to saved figure
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if error_rate is not None:
            data = data[abs(data['error_rate_target'] - error_rate) < 0.01]
            title_suffix = f' at {int(error_rate*100)}% Error Rate'
        else:
            title_suffix = ' (All Error Rates)'
        
        agent_means = data.groupby('agent_type')[metric].mean().sort_values()
        agent_stds = data.groupby('agent_type')[metric].std()
        
        bars = ax.bar(
            range(len(agent_means)),
            agent_means.values,
            yerr=agent_stds.values,
            capsize=5,
            alpha=0.8,
            edgecolor='black',
            linewidth=1.5
        )
        
        for i, bar in enumerate(bars):
            bar.set_color(sns.color_palette('Set2')[i % 8])
        
        ax.set_xticks(range(len(agent_means)))
        ax.set_xticklabels(agent_means.index, fontsize=12)
        ax.set_ylabel(f'{metric.replace("_", " ").title()}', fontsize=14)
        ax.set_title(f'Agent Performance Comparison{title_suffix}', fontsize=16, pad=20)
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        filepath = self.output_dir / f'{save_name}.png'
        plt.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def plot_correlation_matrix(
        self,
        data: pd.DataFrame,
        columns: Optional[List[str]] = None,
        save_name: str = 'correlation_matrix'
    ) -> Path:
        """
        Correlation matrix heatmap.
        
        Args:
            data: DataFrame with data
            columns: Columns to include (None for all numeric)
            save_name: Filename
            
        Returns:
            Path to saved figure
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        
        if columns is None:
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            columns = [c for c in numeric_cols if 'id' not in c.lower()]
        
        corr_matrix = data[columns].corr()
        
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        
        sns.heatmap(
            corr_matrix,
            mask=mask,
            annot=True,
            fmt='.2f',
            cmap='coolwarm',
            center=0,
            square=True,
            ax=ax,
            cbar_kws={'label': 'Correlation Coefficient'}
        )
        
        ax.set_title('Correlation Matrix of Experiment Variables', fontsize=16, pad=20)
        
        plt.tight_layout()
        filepath = self.output_dir / f'{save_name}.png'
        plt.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        return filepath
    
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

