import numpy as np
from typing import Dict, List, Tuple, Optional
from scipy import stats
import pandas as pd


class StatisticalAnalysis:
    """
    Statistical analysis tools for experiment results.
    
    Provides descriptive statistics, correlation analysis,
    hypothesis testing, and confidence intervals.
    """
    
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
    def correlation(
        x: np.ndarray,
        y: np.ndarray,
        method: str = 'pearson'
    ) -> Tuple[float, float]:
        """
        Calculate correlation between two variables.
        
        Args:
            x: First variable
            y: Second variable
            method: Correlation method ('pearson' or 'spearman')
            
        Returns:
            Tuple of (correlation_coefficient, p_value)
            
        Raises:
            ValueError: If method is not supported
        """
        if method == 'pearson':
            corr, pval = stats.pearsonr(x, y)
        elif method == 'spearman':
            corr, pval = stats.spearmanr(x, y)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        return float(corr), float(pval)
    
    @staticmethod
    def confidence_interval(
        data: np.ndarray,
        confidence: float = 0.95
    ) -> Tuple[float, float]:
        """
        Calculate confidence interval for mean.
        
        Args:
            data: Array of values
            confidence: Confidence level (e.g., 0.95 for 95%)
            
        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        n = len(data)
        mean = np.mean(data)
        se = stats.sem(data)
        
        margin = se * stats.t.ppf((1 + confidence) / 2, n - 1)
        
        return float(mean - margin), float(mean + margin)
    
    @staticmethod
    def t_test_independent(
        group1: np.ndarray,
        group2: np.ndarray
    ) -> Tuple[float, float]:
        """
        Perform independent samples t-test.
        
        Tests if two groups have significantly different means.
        
        Args:
            group1: First group of values
            group2: Second group of values
            
        Returns:
            Tuple of (t_statistic, p_value)
        """
        t_stat, pval = stats.ttest_ind(group1, group2)
        return float(t_stat), float(pval)
    
    @staticmethod
    def anova_oneway(groups: List[np.ndarray]) -> Tuple[float, float]:
        """
        Perform one-way ANOVA test.
        
        Tests if multiple groups have significantly different means.
        
        Args:
            groups: List of arrays, one per group
            
        Returns:
            Tuple of (f_statistic, p_value)
        """
        f_stat, pval = stats.f_oneway(*groups)
        return float(f_stat), float(pval)
    
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
    
    @staticmethod
    def linear_regression(
        x: np.ndarray,
        y: np.ndarray
    ) -> Dict[str, float]:
        """
        Perform simple linear regression.
        
        Args:
            x: Independent variable
            y: Dependent variable
            
        Returns:
            Dictionary with slope, intercept, r_squared, p_value
        """
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        
        return {
            'slope': float(slope),
            'intercept': float(intercept),
            'r_squared': float(r_value ** 2),
            'r_value': float(r_value),
            'p_value': float(p_value),
            'std_err': float(std_err)
        }
    
    @staticmethod
    def effect_size_cohens_d(
        group1: np.ndarray,
        group2: np.ndarray
    ) -> float:
        """
        Calculate Cohen's d effect size.
        
        Measures standardized difference between two means.
        
        Args:
            group1: First group
            group2: Second group
            
        Returns:
            Cohen's d value
        """
        n1, n2 = len(group1), len(group2)
        var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
        
        pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
        
        cohens_d = (np.mean(group1) - np.mean(group2)) / pooled_std
        
        return float(cohens_d)
    
    @staticmethod
    def sensitivity_analysis(
        data: pd.DataFrame,
        target_column: str,
        parameter_columns: List[str]
    ) -> pd.DataFrame:
        """
        Perform sensitivity analysis to identify critical parameters.
        
        Calculates correlation of each parameter with target variable.
        
        Args:
            data: DataFrame with experimental data
            target_column: Name of target/output variable
            parameter_columns: List of parameter/input variable names
            
        Returns:
            DataFrame with parameter sensitivity results
        """
        results = []
        
        for param in parameter_columns:
            if param in data.columns:
                corr, pval = StatisticalAnalysis.correlation(
                    data[param].values,
                    data[target_column].values,
                    method='pearson'
                )
                
                results.append({
                    'parameter': param,
                    'correlation': corr,
                    'abs_correlation': abs(corr),
                    'p_value': pval,
                    'significant': pval < 0.05
                })
        
        results_df = pd.DataFrame(results)
        results_df = results_df.sort_values('abs_correlation', ascending=False)
        
        return results_df

