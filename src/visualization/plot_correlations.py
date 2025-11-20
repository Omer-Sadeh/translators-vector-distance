import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Optional

from src.visualization.plot_utils import create_pivot_table, prepare_correlation_columns


def plot_agent_comparison_heatmap(
    output_dir: Path,
    dpi: int,
    data: pd.DataFrame,
    metric: str = 'cosine_distance',
    save_name: str = 'agent_comparison'
) -> Path:
    """Heatmap: Agent comparison across error rates."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    pivot = create_pivot_table(data, metric, 'agent_type', 'error_rate_target')
    
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
    filepath = output_dir / f'{save_name}.png'
    plt.savefig(filepath, dpi=dpi, bbox_inches='tight')
    plt.close()
    
    return filepath


def plot_correlation_matrix(
    output_dir: Path,
    dpi: int,
    data: pd.DataFrame,
    columns: Optional[list] = None,
    save_name: str = 'correlation_matrix'
) -> Path:
    """Correlation matrix heatmap."""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    columns = prepare_correlation_columns(data, columns)
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
    filepath = output_dir / f'{save_name}.png'
    plt.savefig(filepath, dpi=dpi, bbox_inches='tight')
    plt.close()
    
    return filepath

