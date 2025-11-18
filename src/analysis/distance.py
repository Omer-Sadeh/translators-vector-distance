import numpy as np
from typing import Union
from scipy.spatial import distance as scipy_distance


class DistanceMetrics:
    """
    Distance metric calculations for vector embeddings.
    
    Provides cosine, Euclidean, and Manhattan distance metrics.
    All methods support both single pairs and batch calculations.
    """
    
    @staticmethod
    def cosine(
        embedding1: np.ndarray,
        embedding2: np.ndarray
    ) -> Union[float, np.ndarray]:
        """
        Calculate cosine distance between embeddings.
        
        Cosine distance = 1 - cosine similarity
        Range: [0, 2], where 0 = identical, 2 = opposite
        
        Args:
            embedding1: First embedding(s), shape [d] or [n, d]
            embedding2: Second embedding(s), shape [d] or [n, d]
            
        Returns:
            Cosine distance value(s)
            
        Raises:
            ValueError: If embedding shapes don't match
        """
        if embedding1.shape != embedding2.shape:
            raise ValueError(
                f"Embedding shapes must match: {embedding1.shape} vs {embedding2.shape}"
            )
        
        if embedding1.ndim == 1:
            return scipy_distance.cosine(embedding1, embedding2)
        else:
            distances = np.array([
                scipy_distance.cosine(e1, e2)
                for e1, e2 in zip(embedding1, embedding2)
            ])
            return distances
    
    @staticmethod
    def euclidean(
        embedding1: np.ndarray,
        embedding2: np.ndarray
    ) -> Union[float, np.ndarray]:
        """
        Calculate Euclidean (L2) distance between embeddings.
        
        Euclidean distance = sqrt(sum((x1 - x2)^2))
        
        Args:
            embedding1: First embedding(s), shape [d] or [n, d]
            embedding2: Second embedding(s), shape [d] or [n, d]
            
        Returns:
            Euclidean distance value(s)
            
        Raises:
            ValueError: If embedding shapes don't match
        """
        if embedding1.shape != embedding2.shape:
            raise ValueError(
                f"Embedding shapes must match: {embedding1.shape} vs {embedding2.shape}"
            )
        
        if embedding1.ndim == 1:
            return scipy_distance.euclidean(embedding1, embedding2)
        else:
            distances = np.array([
                scipy_distance.euclidean(e1, e2)
                for e1, e2 in zip(embedding1, embedding2)
            ])
            return distances
    
    @staticmethod
    def manhattan(
        embedding1: np.ndarray,
        embedding2: np.ndarray
    ) -> Union[float, np.ndarray]:
        """
        Calculate Manhattan (L1) distance between embeddings.
        
        Manhattan distance = sum(abs(x1 - x2))
        
        Args:
            embedding1: First embedding(s), shape [d] or [n, d]
            embedding2: Second embedding(s), shape [d] or [n, d]
            
        Returns:
            Manhattan distance value(s)
            
        Raises:
            ValueError: If embedding shapes don't match
        """
        if embedding1.shape != embedding2.shape:
            raise ValueError(
                f"Embedding shapes must match: {embedding1.shape} vs {embedding2.shape}"
            )
        
        if embedding1.ndim == 1:
            return scipy_distance.cityblock(embedding1, embedding2)
        else:
            distances = np.array([
                scipy_distance.cityblock(e1, e2)
                for e1, e2 in zip(embedding1, embedding2)
            ])
            return distances
    
    @staticmethod
    def all_metrics(
        embedding1: np.ndarray,
        embedding2: np.ndarray
    ) -> dict:
        """
        Calculate all distance metrics at once.
        
        Args:
            embedding1: First embedding(s)
            embedding2: Second embedding(s)
            
        Returns:
            Dictionary with keys: 'cosine', 'euclidean', 'manhattan'
        """
        return {
            'cosine': DistanceMetrics.cosine(embedding1, embedding2),
            'euclidean': DistanceMetrics.euclidean(embedding1, embedding2),
            'manhattan': DistanceMetrics.manhattan(embedding1, embedding2)
        }

