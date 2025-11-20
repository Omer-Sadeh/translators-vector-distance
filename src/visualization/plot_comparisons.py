import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pathlib import Path
from typing import Optional

from src.visualization.plot_utils import (
    add_word_count_if_missing,
    filter_by_error_rate,
    aggregate_by_group
)


def plot_sentence_length_effect(
    output_dir: Path,
    dpi: int,
    data: pd.DataFrame,
    metric: str = 'cosine_distance',
    save_name: str = 'length_effect'
) -> Path:
    """Scatter plot: Sentence length vs distance, colored by error rate."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    data = add_word_count_if_missing(data)
    
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
    filepath = output_dir / f'{save_name}.png'
    plt.savefig(filepath, dpi=dpi, bbox_inches='tight')
    plt.close()
    
    return filepath


def plot_agent_performance_bars(
    output_dir: Path,
    dpi: int,
    data: pd.DataFrame,
    metric: str = 'cosine_distance',
    error_rate: Optional[float] = None,
    save_name: str = 'agent_performance'
) -> Path:
    """Bar chart: Performance comparison across agents."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    if error_rate is not None:
        data = filter_by_error_rate(data, error_rate)
        title_suffix = f' at {int(error_rate*100)}% Error Rate'
    else:
        title_suffix = ' (All Error Rates)'
    
    agent_means, agent_stds = aggregate_by_group(data, 'agent_type', metric)
    
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
    filepath = output_dir / f'{save_name}.png'
    plt.savefig(filepath, dpi=dpi, bbox_inches='tight')
    plt.close()
    
    return filepath

