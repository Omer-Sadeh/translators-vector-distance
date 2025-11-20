import numpy as np
import pandas as pd
from typing import Dict


class DescriptiveStatistics:
    """Descriptive statistics tools for experiment results."""
    
    @staticmethod
    def descriptive_stats(data: np.ndarray) -> Dict[str, float]:
        """
        Calculate descriptive statistics.
        
        Args:
            data: Array of values
            
        Returns:
            Dictionary with mean, median, std, min, max, quartiles
        """
        return {
            'mean': float(np.mean(data)),
            'median': float(np.median(data)),
            'std': float(np.std(data, ddof=1)),
            'min': float(np.min(data)),
            'max': float(np.max(data)),
            'q25': float(np.percentile(data, 25)),
            'q75': float(np.percentile(data, 75)),
            'count': len(data)
        }
    
    @staticmethod
    def group_statistics(
        data: pd.DataFrame,
        group_column: str,
        value_column: str
    ) -> pd.DataFrame:
        """
        Calculate statistics grouped by category.
        
        Args:
            data: DataFrame with data
            group_column: Column name for grouping
            value_column: Column name for values
            
        Returns:
            DataFrame with statistics per group
        """
        grouped = data.groupby(group_column)[value_column].agg([
            ('count', 'count'),
            ('mean', 'mean'),
            ('median', 'median'),
            ('std', 'std'),
            ('min', 'min'),
            ('max', 'max'),
            ('q25', lambda x: x.quantile(0.25)),
            ('q75', lambda x: x.quantile(0.75))
        ])
        
        return grouped

