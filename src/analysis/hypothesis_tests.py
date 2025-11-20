import numpy as np
from typing import Tuple, List
from scipy import stats


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


def t_test_paired(
    group1: np.ndarray,
    group2: np.ndarray
) -> Tuple[float, float]:
    """
    Perform paired samples t-test.
    
    Tests if two related groups have significantly different means.
    
    Args:
        group1: First group of values
        group2: Second group of values (paired with group1)
        
    Returns:
        Tuple of (t_statistic, p_value)
    """
    t_stat, pval = stats.ttest_rel(group1, group2)
    return float(t_stat), float(pval)


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


def chi_square_test(
    observed: np.ndarray,
    expected: np.ndarray = None
) -> Tuple[float, float]:
    """
    Perform chi-square goodness of fit test.
    
    Args:
        observed: Observed frequencies
        expected: Expected frequencies (None for uniform distribution)
        
    Returns:
        Tuple of (chi_square_statistic, p_value)
    """
    if expected is None:
        chi_stat, pval = stats.chisquare(observed)
    else:
        chi_stat, pval = stats.chisquare(observed, expected)
    
    return float(chi_stat), float(pval)


def mann_whitney_u_test(
    group1: np.ndarray,
    group2: np.ndarray
) -> Tuple[float, float]:
    """
    Perform Mann-Whitney U test (non-parametric alternative to t-test).
    
    Args:
        group1: First group of values
        group2: Second group of values
        
    Returns:
        Tuple of (u_statistic, p_value)
    """
    u_stat, pval = stats.mannwhitneyu(group1, group2)
    return float(u_stat), float(pval)


def kruskal_wallis_test(groups: List[np.ndarray]) -> Tuple[float, float]:
    """
    Perform Kruskal-Wallis H test (non-parametric alternative to ANOVA).
    
    Args:
        groups: List of arrays, one per group
        
    Returns:
        Tuple of (h_statistic, p_value)
    """
    h_stat, pval = stats.kruskal(*groups)
    return float(h_stat), float(pval)


def shapiro_wilk_test(data: np.ndarray) -> Tuple[float, float]:
    """
    Perform Shapiro-Wilk test for normality.
    
    Args:
        data: Array of values
        
    Returns:
        Tuple of (w_statistic, p_value)
    """
    w_stat, pval = stats.shapiro(data)
    return float(w_stat), float(pval)


def levene_test(groups: List[np.ndarray]) -> Tuple[float, float]:
    """
    Perform Levene test for homogeneity of variances.
    
    Args:
        groups: List of arrays, one per group
        
    Returns:
        Tuple of (w_statistic, p_value)
    """
    w_stat, pval = stats.levene(*groups)
    return float(w_stat), float(pval)

