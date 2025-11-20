import logging
from typing import Optional, Dict
import numpy as np

from src.translation.chain import TranslationChain
from src.analysis.embeddings import EmbeddingEngine
from src.analysis.distance import DistanceMetrics
from src.data.storage import ExperimentStorage


logger = logging.getLogger(__name__)


class ExperimentExecutor:
    """Executes individual experiments: translation chain + analysis."""
    
    def __init__(
        self,
        translation_chain: TranslationChain,
        embedding_engine: EmbeddingEngine,
        storage: ExperimentStorage
    ):
        """
        Initialize experiment executor.
        
        Args:
            translation_chain: Configured translation chain
            embedding_engine: Embedding engine for vector calculation
            storage: Storage backend for results
        """
        self.translation_chain = translation_chain
        self.embedding_engine = embedding_engine
        self.storage = storage
    
    def execute_single(
        self,
        sentence: str,
        error_rate: float
    ) -> Optional[int]:
        """
        Execute single experiment: translation chain + analysis.
        
        Args:
            sentence: Original English sentence
            error_rate: Target error rate (0.0 to 1.0)
            
        Returns:
            Experiment ID if successful, None otherwise
        """
        try:
            logger.info(f"Running experiment: error_rate={error_rate}")
            
            chain_result = self.translation_chain.execute_chain(sentence, error_rate)
            
            if not chain_result.success:
                logger.warning(f"Translation chain failed: {chain_result.error_message}")
                return None
            
            embeddings = self._calculate_embeddings(sentence, chain_result.translation_en)
            distances = self._calculate_distances(embeddings['original'], embeddings['final'])
            
            experiment_id = self._store_results(sentence, chain_result, embeddings, distances)
            
            logger.info(
                f"Experiment {experiment_id} completed: "
                f"cosine_distance={distances['cosine']:.4f}"
            )
            
            return experiment_id
            
        except Exception as e:
            logger.error(f"Experiment failed: {str(e)}", exc_info=True)
            return None
    
    def _calculate_embeddings(
        self,
        original: str,
        final: str
    ) -> Dict[str, np.ndarray]:
        """Calculate embeddings for original and final texts."""
        return {
            'original': self.embedding_engine.encode(original),
            'final': self.embedding_engine.encode(final)
        }
    
    def _calculate_distances(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray
    ) -> Dict[str, float]:
        """Calculate distance metrics between embeddings."""
        return DistanceMetrics.all_metrics(embedding1, embedding2)
    
    def _store_results(
        self,
        sentence: str,
        chain_result,
        embeddings: Dict[str, np.ndarray],
        distances: Dict[str, float]
    ) -> int:
        """Store experiment results in database."""
        sentence_id = self.storage.get_or_create_sentence(sentence)
        experiment_id = self.storage.store_experiment(
            sentence_id,
            chain_result,
            embeddings,
            distances
        )
        return experiment_id

