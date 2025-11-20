import numpy as np
import pandas as pd
from scipy import stats


def calculate_confidence_interval(data: pd.Series, confidence: float = 0.95) -> tuple:
    """
    Calculate confidence interval for grouped data.
    
    Args:
        data: Series with values
        confidence: Confidence level (default 0.95)
        
    Returns:
        Tuple of (lower_bound, upper_bound) arrays
    """
    mean = data['mean']
    std = data['std']
    count = data['count']
    
    ci = 1.96 * std / np.sqrt(count)
    
    return mean - ci, mean + ci


def format_error_rate_labels(error_rates: np.ndarray) -> list:
    """
    Format error rates as percentage labels.
    
    Args:
        error_rates: Array of error rates (0.0 to 1.0)
        
    Returns:
        List of formatted labels
    """
    return [f'{int(rate * 100)}%' for rate in error_rates]


def add_word_count_if_missing(data: pd.DataFrame) -> pd.DataFrame:
    """
    Add word_count column if missing by counting words in original_text.
    
    Args:
        data: DataFrame with data
        
    Returns:
        DataFrame with word_count column
    """
    if 'word_count' not in data.columns and 'original_text' in data.columns:
        data = data.copy()
        data['word_count'] = data['original_text'].str.split().str.len()
    
    return data


def prepare_correlation_columns(data: pd.DataFrame, columns: list = None) -> list:
    """
    Prepare columns for correlation matrix.
    
    Args:
        data: DataFrame with data
        columns: Optional list of columns
        
    Returns:
        List of column names for correlation
    """
    if columns is None:
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        columns = [c for c in numeric_cols if 'id' not in c.lower()]
    
    return columns


def create_pivot_table(
    data: pd.DataFrame,
    values: str,
    index: str,
    columns: str,
    aggfunc: str = 'mean'
) -> pd.DataFrame:
    """
    Create pivot table with formatted columns.
    
    Args:
        data: DataFrame with data
        values: Column for values
        index: Column for index
        columns: Column for columns
        aggfunc: Aggregation function
        
    Returns:
        Pivot table DataFrame
    """
    pivot = data.pivot_table(
        values=values,
        index=index,
        columns=columns,
        aggfunc=aggfunc
    )
    
    if columns == 'error_rate_target':
        pivot.columns = [f'{int(c*100)}%' for c in pivot.columns]
    
    return pivot


def filter_by_error_rate(
    data: pd.DataFrame,
    error_rate: float,
    tolerance: float = 0.01
) -> pd.DataFrame:
    """
    Filter data by specific error rate.
    
    Args:
        data: DataFrame with data
        error_rate: Target error rate
        tolerance: Tolerance for matching
        
    Returns:
        Filtered DataFrame
    """
    return data[abs(data['error_rate_target'] - error_rate) < tolerance]


def aggregate_by_group(
    data: pd.DataFrame,
    group_column: str,
    value_column: str
) -> tuple:
    """
    Aggregate data by group.
    
    Args:
        data: DataFrame with data
        group_column: Column to group by
        value_column: Column to aggregate
        
    Returns:
        Tuple of (means, stds) Series
    """
    means = data.groupby(group_column)[value_column].mean().sort_values()
    stds = data.groupby(group_column)[value_column].std()
    
    return means, stds

