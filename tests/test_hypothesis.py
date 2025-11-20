import pytest
import numpy as np
from scipy import stats

from src.analysis.hypothesis_tests import (
    t_test_independent,
    anova_oneway,
    chi_square_test,
    mann_whitney_u_test
)


class TestHypothesisTests:
    """Tests for hypothesis testing functions."""
    
    def test_t_test_independent_different_groups(self):
        """Test independent t-test with different groups."""
        group1 = np.array([1, 2, 3, 4, 5])
        group2 = np.array([6, 7, 8, 9, 10])
        
        t_stat, p_value = t_test_independent(group1, group2)
        
        assert isinstance(t_stat, float)
        assert isinstance(p_value, float)
        assert p_value < 0.05  # Should be significantly different
    
    def test_t_test_independent_same_groups(self):
        """Test independent t-test with identical groups."""
        group1 = np.array([1, 2, 3, 4, 5])
        group2 = np.array([1, 2, 3, 4, 5])
        
        t_stat, p_value = t_test_independent(group1, group2)
        
        assert abs(t_stat) < 0.001  # Should be nearly zero
        assert p_value > 0.05  # Should not be significant
    
    def test_t_test_independent_similar_groups(self):
        """Test t-test with similar but not identical groups."""
        np.random.seed(42)
        group1 = np.random.normal(10, 2, 100)
        group2 = np.random.normal(10.5, 2, 100)
        
        t_stat, p_value = t_test_independent(group1, group2)
        
        assert isinstance(t_stat, float)
        assert isinstance(p_value, float)
    
    def test_anova_oneway_three_groups(self):
        """Test one-way ANOVA with three groups."""
        group1 = np.array([1, 2, 3, 4, 5])
        group2 = np.array([2, 3, 4, 5, 6])
        group3 = np.array([5, 6, 7, 8, 9])
        
        f_stat, p_value = anova_oneway([group1, group2, group3])
        
        assert isinstance(f_stat, float)
        assert isinstance(p_value, float)
        assert f_stat > 0
        assert p_value < 0.05  # Groups should be significantly different
    
    def test_anova_oneway_identical_groups(self):
        """Test ANOVA with identical groups."""
        group1 = np.array([1, 2, 3, 4, 5])
        group2 = np.array([1, 2, 3, 4, 5])
        group3 = np.array([1, 2, 3, 4, 5])
        
        f_stat, p_value = anova_oneway([group1, group2, group3])
        
        assert abs(f_stat) < 0.001
        assert p_value > 0.05
    
    def test_anova_oneway_two_groups(self):
        """Test ANOVA with only two groups."""
        group1 = np.array([1, 2, 3])
        group2 = np.array([4, 5, 6])
        
        f_stat, p_value = anova_oneway([group1, group2])
        
        assert isinstance(f_stat, float)
        assert isinstance(p_value, float)
    
    def test_chi_square_test_independent(self):
        """Test chi-square test with independent categories."""
        observed = np.array([10, 10, 20, 20, 20, 20])
        expected = np.array([16, 16, 17, 17, 17, 17])
        
        chi2_stat, p_value = chi_square_test(observed, expected)
        
        assert isinstance(chi2_stat, float)
        assert isinstance(p_value, float)
        assert chi2_stat >= 0
    
    def test_chi_square_test_dependent(self):
        """Test chi-square with strong dependence."""
        observed = np.array([50, 5, 5, 50])
        expected = np.array([27.5, 27.5, 27.5, 27.5])
        
        chi2_stat, p_value = chi_square_test(observed, expected)
        
        assert chi2_stat > 10
        assert p_value < 0.05
    
    def test_chi_square_test_uniform(self):
        """Test chi-square with uniform distribution."""
        observed = np.array([25, 25, 25, 25])
        
        chi2_stat, p_value = chi_square_test(observed)
        
        assert chi2_stat < 0.01
        assert p_value > 0.9
    
    def test_mann_whitney_u_test_different_distributions(self):
        """Test Mann-Whitney U test with different distributions."""
        group1 = np.array([1, 2, 3, 4, 5])
        group2 = np.array([6, 7, 8, 9, 10])
        
        u_stat, p_value = mann_whitney_u_test(group1, group2)
        
        assert isinstance(u_stat, float)
        assert isinstance(p_value, float)
        assert p_value < 0.05
    
    def test_mann_whitney_u_test_same_distribution(self):
        """Test Mann-Whitney U with same distribution."""
        group1 = np.array([1, 2, 3, 4, 5])
        group2 = np.array([1, 2, 3, 4, 5])
        
        u_stat, p_value = mann_whitney_u_test(group1, group2)
        
        assert p_value > 0.05
    
    def test_mann_whitney_u_test_overlapping(self):
        """Test Mann-Whitney U with overlapping distributions."""
        np.random.seed(42)
        group1 = np.random.normal(10, 2, 50)
        group2 = np.random.normal(11, 2, 50)
        
        u_stat, p_value = mann_whitney_u_test(group1, group2)
        
        assert isinstance(u_stat, float)
        assert isinstance(p_value, float)

