import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path


def plot_error_rate_vs_distance(
    output_dir: Path,
    dpi: int,
    data: pd.DataFrame,
    metric: str = 'cosine_distance',
    save_name: str = 'error_vs_distance'
) -> Path:
    """Line plot: Error rate vs vector distance with confidence intervals."""
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
    filepath = output_dir / f'{save_name}.png'
    plt.savefig(filepath, dpi=dpi, bbox_inches='tight')
    plt.close()
    
    return filepath

