from src.analysis.statistics_descriptive import DescriptiveStatistics
from src.analysis.statistics_inferential import InferentialStatistics


class StatisticalAnalysis:
    """
    Unified interface for statistical analysis tools.
    
    Combines descriptive and inferential statistics methods.
    """
    
    descriptive_stats = DescriptiveStatistics.descriptive_stats
    group_statistics = DescriptiveStatistics.group_statistics
    
    correlation = InferentialStatistics.correlation
    confidence_interval = InferentialStatistics.confidence_interval
    t_test_independent = InferentialStatistics.t_test_independent
    anova_oneway = InferentialStatistics.anova_oneway
    linear_regression = InferentialStatistics.linear_regression
    effect_size_cohens_d = InferentialStatistics.effect_size_cohens_d
    sensitivity_analysis = InferentialStatistics.sensitivity_analysis
