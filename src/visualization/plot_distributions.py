import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pathlib import Path


def plot_distance_distributions(
    output_dir: Path,
    dpi: int,
    data: pd.DataFrame,
    metric: str = 'cosine_distance',
    save_name: str = 'distance_distributions'
) -> Path:
    """Box plot: Distribution of distances per error rate."""
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
    filepath = output_dir / f'{save_name}.png'
    plt.savefig(filepath, dpi=dpi, bbox_inches='tight')
    plt.close()
    
    return filepath

