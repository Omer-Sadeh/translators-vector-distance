import numpy as np
import pandas as pd
from typing import Dict, Tuple, List
from scipy import stats

from src.analysis.hypothesis_tests import (
    t_test_independent,
    anova_oneway
)


class InferentialStatistics:
    """Inferential statistics and hypothesis testing tools."""
    
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
        """Perform independent samples t-test."""
        return t_test_independent(group1, group2)
    
    @staticmethod
    def anova_oneway(groups: List[np.ndarray]) -> Tuple[float, float]:
        """Perform one-way ANOVA test."""
        return anova_oneway(groups)
    
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
                corr, pval = InferentialStatistics.correlation(
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
        
        if not results:
            return pd.DataFrame(columns=['parameter', 'correlation', 'abs_correlation', 'p_value', 'significant'])
        
        results_df = pd.DataFrame(results)
        results_df = results_df.sort_values('abs_correlation', ascending=False)
        
        return results_df

