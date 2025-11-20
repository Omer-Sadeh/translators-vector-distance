import pytest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch

from src.analysis.embeddings import EmbeddingEngine
from src.analysis.distance import DistanceMetrics
from src.analysis.statistics import StatisticalAnalysis


class TestEmbeddingEngine:
    """Tests for EmbeddingEngine."""
    
    @patch('src.analysis.embeddings.SentenceTransformer')
    def test_initialization(self, mock_model):
        """Test embedding engine initialization."""
        engine = EmbeddingEngine()
        assert engine.model_name == 'all-MiniLM-L6-v2'
        assert engine.device == 'cpu'
        assert engine.batch_size == 32
    
    @patch('src.analysis.embeddings.SentenceTransformer')
    def test_encode_single_text(self, mock_model):
        """Test encoding single text."""
        mock_model_instance = Mock()
        mock_model_instance.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        mock_model.return_value = mock_model_instance
        
        engine = EmbeddingEngine()
        result = engine.encode("Hello world")
        
        assert isinstance(result, np.ndarray)
        assert result.shape == (3,)
    
    @patch('src.analysis.embeddings.SentenceTransformer')
    def test_encode_multiple_texts(self, mock_model):
        """Test encoding multiple texts."""
        mock_model_instance = Mock()
        mock_model_instance.encode.return_value = np.array([
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6]
        ])
        mock_model.return_value = mock_model_instance
        
        engine = EmbeddingEngine()
        result = engine.encode(["Hello", "World"])
        
        assert isinstance(result, np.ndarray)
        assert result.shape == (2, 3)
    
    @patch('src.analysis.embeddings.SentenceTransformer')
    def test_cache_functionality(self, mock_model):
        """Test embedding cache."""
        mock_model_instance = Mock()
        mock_model_instance.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        mock_model.return_value = mock_model_instance
        
        engine = EmbeddingEngine()
        
        # First call - should use model
        engine.encode("Hello", use_cache=True)
        assert engine.get_cache_size() == 1
        
        # Second call - should use cache
        engine.encode("Hello", use_cache=True)
        # Model should only be called once
        assert mock_model_instance.encode.call_count == 1
    
    @patch('src.analysis.embeddings.SentenceTransformer')
    def test_clear_cache(self, mock_model):
        """Test clearing cache."""
        mock_model_instance = Mock()
        mock_model_instance.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        mock_model.return_value = mock_model_instance
        
        engine = EmbeddingEngine()
        engine.encode("Hello", use_cache=True)
        assert engine.get_cache_size() == 1
        
        engine.clear_cache()
        assert engine.get_cache_size() == 0


class TestDistanceMetrics:
    """Tests for DistanceMetrics."""
    
    def test_cosine_distance_identical(self):
        """Test cosine distance for identical vectors."""
        v1 = np.array([1.0, 0.0, 0.0])
        v2 = np.array([1.0, 0.0, 0.0])
        distance = DistanceMetrics.cosine(v1, v2)
        assert abs(distance) < 1e-6
    
    def test_cosine_distance_opposite(self):
        """Test cosine distance for opposite vectors."""
        v1 = np.array([1.0, 0.0, 0.0])
        v2 = np.array([-1.0, 0.0, 0.0])
        distance = DistanceMetrics.cosine(v1, v2)
        assert abs(distance - 2.0) < 1e-6
    
    def test_cosine_distance_orthogonal(self):
        """Test cosine distance for orthogonal vectors."""
        v1 = np.array([1.0, 0.0, 0.0])
        v2 = np.array([0.0, 1.0, 0.0])
        distance = DistanceMetrics.cosine(v1, v2)
        assert abs(distance - 1.0) < 1e-6
    
    def test_euclidean_distance(self):
        """Test Euclidean distance."""
        v1 = np.array([0.0, 0.0, 0.0])
        v2 = np.array([1.0, 1.0, 1.0])
        distance = DistanceMetrics.euclidean(v1, v2)
        expected = np.sqrt(3.0)
        assert abs(distance - expected) < 1e-6
    
    def test_manhattan_distance(self):
        """Test Manhattan distance."""
        v1 = np.array([0.0, 0.0, 0.0])
        v2 = np.array([1.0, 1.0, 1.0])
        distance = DistanceMetrics.manhattan(v1, v2)
        assert abs(distance - 3.0) < 1e-6
    
    def test_distance_shape_mismatch(self):
        """Test distance with mismatched shapes."""
        v1 = np.array([1.0, 0.0])
        v2 = np.array([1.0, 0.0, 0.0])
        
        with pytest.raises(ValueError, match="Embedding shapes must match"):
            DistanceMetrics.cosine(v1, v2)
    
    def test_all_metrics(self):
        """Test computing all metrics at once."""
        v1 = np.array([1.0, 0.0, 0.0])
        v2 = np.array([0.0, 1.0, 0.0])
        
        distances = DistanceMetrics.all_metrics(v1, v2)
        
        assert 'cosine' in distances
        assert 'euclidean' in distances
        assert 'manhattan' in distances
    
    def test_batch_distances(self):
        """Test batch distance calculation."""
        v1 = np.array([[1.0, 0.0], [0.0, 1.0]])
        v2 = np.array([[1.0, 0.0], [0.0, 1.0]])
        
        distances = DistanceMetrics.cosine(v1, v2)
        assert distances.shape == (2,)
        assert all(abs(d) < 1e-6 for d in distances)


class TestStatisticalAnalysis:
    """Tests for StatisticalAnalysis."""
    
    def test_descriptive_stats(self):
        """Test descriptive statistics."""
        data = np.array([1, 2, 3, 4, 5])
        stats = StatisticalAnalysis.descriptive_stats(data)
        
        assert stats['mean'] == 3.0
        assert stats['median'] == 3.0
        assert stats['min'] == 1.0
        assert stats['max'] == 5.0
        assert stats['count'] == 5
    
    def test_correlation_pearson(self):
        """Test Pearson correlation."""
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([2, 4, 6, 8, 10])
        
        corr, pval = StatisticalAnalysis.correlation(x, y, method='pearson')
        
        assert abs(corr - 1.0) < 1e-6  # Perfect correlation
        assert pval < 0.05  # Significant
    
    def test_correlation_spearman(self):
        """Test Spearman correlation."""
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([1, 4, 9, 16, 25])  # Monotonic but not linear
        
        corr, pval = StatisticalAnalysis.correlation(x, y, method='spearman')
        
        assert abs(corr - 1.0) < 1e-6  # Perfect monotonic correlation
    
    def test_confidence_interval(self):
        """Test confidence interval calculation."""
        data = np.array([1, 2, 3, 4, 5])
        lower, upper = StatisticalAnalysis.confidence_interval(data, confidence=0.95)
        
        mean = np.mean(data)
        assert lower < mean < upper
    
    def test_t_test_independent(self):
        """Test independent t-test."""
        group1 = np.array([1, 2, 3, 4, 5])
        group2 = np.array([6, 7, 8, 9, 10])
        
        t_stat, pval = StatisticalAnalysis.t_test_independent(group1, group2)
        
        assert pval < 0.05  # Significantly different
    
    def test_linear_regression(self):
        """Test linear regression."""
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([2, 4, 6, 8, 10])
        
        results = StatisticalAnalysis.linear_regression(x, y)
        
        assert abs(results['slope'] - 2.0) < 1e-6
        assert abs(results['intercept']) < 1e-6
        assert abs(results['r_squared'] - 1.0) < 1e-6
    
    def test_cohens_d(self):
        """Test Cohen's d effect size."""
        group1 = np.array([1, 2, 3])
        group2 = np.array([4, 5, 6])
        
        d = StatisticalAnalysis.effect_size_cohens_d(group1, group2)
        assert d < 0  # group1 mean < group2 mean
    
    def test_anova_oneway(self):
        """Test one-way ANOVA."""
        group1 = np.array([1, 2, 3, 4, 5])
        group2 = np.array([6, 7, 8, 9, 10])
        group3 = np.array([11, 12, 13, 14, 15])
        
        f_stat, pval = StatisticalAnalysis.anova_oneway([group1, group2, group3])
        
        assert f_stat > 0
        assert pval < 0.05  # Significantly different
    
    def test_anova_with_same_groups(self):
        """Test ANOVA with identical groups."""
        group1 = np.array([5, 5, 5, 5, 5])
        group2 = np.array([5, 5, 5, 5, 5])
        
        f_stat, pval = StatisticalAnalysis.anova_oneway([group1, group2])
        
        # With identical groups, p-value may be NaN; check if NaN or > 0.05
        assert np.isnan(pval) or pval > 0.05
    
    def test_group_statistics(self):
        """Test grouped statistics calculation."""
        data = pd.DataFrame({
            'agent': ['cursor', 'cursor', 'gemini', 'gemini', 'claude', 'claude'],
            'distance': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
        })
        
        grouped = StatisticalAnalysis.group_statistics(data, 'agent', 'distance')
        
        assert len(grouped) == 3
        assert 'mean' in grouped.columns
        assert 'median' in grouped.columns
        assert 'count' in grouped.columns
    
    def test_linear_regression_perfect_fit(self):
        """Test regression with perfect fit."""
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([2, 4, 6, 8, 10])
        
        results = StatisticalAnalysis.linear_regression(x, y)
        
        assert abs(results['slope'] - 2.0) < 1e-10
        assert abs(results['r_squared'] - 1.0) < 1e-10
        assert results['p_value'] < 0.05
    
    def test_linear_regression_no_relationship(self):
        """Test regression with no relationship."""
        np.random.seed(42)
        x = np.random.rand(100)
        y = np.random.rand(100)
        
        results = StatisticalAnalysis.linear_regression(x, y)
        
        assert abs(results['r_squared']) < 0.5  # Weak relationship
    
    def test_sensitivity_analysis(self):
        """Test sensitivity analysis."""
        data = pd.DataFrame({
            'error_rate': [0.0, 0.1, 0.2, 0.3, 0.4],
            'sentence_length': [15, 20, 25, 30, 35],
            'distance': [0.1, 0.2, 0.3, 0.4, 0.5]
        })
        
        results = StatisticalAnalysis.sensitivity_analysis(
            data,
            'distance',
            ['error_rate', 'sentence_length']
        )
        
        assert len(results) == 2
        assert 'parameter' in results.columns
        assert 'correlation' in results.columns
        assert 'p_value' in results.columns
        assert 'significant' in results.columns
    
    def test_sensitivity_analysis_missing_column(self):
        """Test sensitivity analysis with missing parameter."""
        data = pd.DataFrame({
            'distance': [0.1, 0.2, 0.3, 0.4, 0.5]
        })
        
        results = StatisticalAnalysis.sensitivity_analysis(
            data,
            'distance',
            ['error_rate', 'nonexistent']
        )
        
        # Should return empty dataframe with proper columns
        assert isinstance(results, pd.DataFrame)
        assert len(results) == 0 or 'parameter' in results.columns
    
    def test_confidence_interval_narrow(self):
        """Test confidence interval with low variance."""
        data = np.array([5.0, 5.1, 4.9, 5.0, 5.1])
        lower, upper = StatisticalAnalysis.confidence_interval(data, confidence=0.95)
        
        mean = np.mean(data)
        assert lower < mean < upper
        assert (upper - lower) < 1.0  # Narrow interval
    
    def test_confidence_interval_wide(self):
        """Test confidence interval with high variance."""
        data = np.array([1.0, 5.0, 2.0, 8.0, 3.0])
        lower, upper = StatisticalAnalysis.confidence_interval(data, confidence=0.95)
        
        mean = np.mean(data)
        assert lower < mean < upper
        assert (upper - lower) > 1.0  # Wide interval
    
    def test_correlation_invalid_method(self):
        """Test correlation with invalid method."""
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([2, 4, 6, 8, 10])
        
        with pytest.raises(ValueError, match="Unsupported method"):
            StatisticalAnalysis.correlation(x, y, method='invalid')
    
    def test_descriptive_stats_single_value(self):
        """Test descriptive stats with single value."""
        data = np.array([5.0])
        stats = StatisticalAnalysis.descriptive_stats(data)
        
        assert stats['mean'] == 5.0
        assert stats['median'] == 5.0
        assert stats['min'] == 5.0
        assert stats['max'] == 5.0
        assert stats['count'] == 1
    
    def test_t_test_same_groups(self):
        """Test t-test with identical groups."""
        group1 = np.array([5, 5, 5, 5, 5])
        group2 = np.array([5, 5, 5, 5, 5])
        
        t_stat, pval = StatisticalAnalysis.t_test_independent(group1, group2)
        
        # With identical groups, p-value may be NaN; check if NaN or > 0.05
        assert np.isnan(pval) or pval > 0.05
    
    def test_effect_size_identical_groups(self):
        """Test Cohen's d with identical groups."""
        group1 = np.array([5, 5, 5, 5, 5])
        group2 = np.array([5, 5, 5, 5, 5])
        
        d = StatisticalAnalysis.effect_size_cohens_d(group1, group2)
        # With identical groups, pooled std is 0, result may be NaN
        assert np.isnan(d) or abs(d) < 1e-10
    
    def test_group_statistics_empty_group(self):
        """Test grouped statistics with empty result."""
        data = pd.DataFrame({
            'agent': [],
            'distance': []
        })
        
        grouped = StatisticalAnalysis.group_statistics(data, 'agent', 'distance')
        
        assert len(grouped) == 0

