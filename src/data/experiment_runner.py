from typing import List, Dict, Optional
from pathlib import Path
import logging

from src.agents.factory import AgentFactory
from src.translation.chain import TranslationChain
from src.translation.error_injector import ErrorInjector
from src.analysis.embeddings import EmbeddingEngine
from src.data.generator import SentenceGenerator
from src.data.storage import ExperimentStorage
from src.data.experiment_executor import ExperimentExecutor
from src.config import get_settings


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExperimentRunner:
    """
    Orchestrates complete experiment execution.
    
    Manages the full pipeline: sentence generation, translation chains,
    embedding calculation, distance measurement, and result storage.
    """
    
    def __init__(
        self,
        agent_type: str,
        config_path: Optional[str] = None
    ):
        """
        Initialize experiment runner.
        
        Args:
            agent_type: Type of agent to use ('cursor', 'gemini', 'claude', 'ollama')
            config_path: Optional path to config file
        """
        self.settings = get_settings(config_path)
        self.agent_type = agent_type
        
        agent_config = self.settings.get_agent_config(agent_type)
        self.agent = AgentFactory.create(agent_type, agent_config)
        
        self.error_injector = ErrorInjector()
        self.translation_chain = TranslationChain(self.agent, self.error_injector)
        
        embedding_config = {
            'model_name': self.settings.get_embedding_model(),
            'device': self.settings.get('embeddings.device', 'cpu'),
            'batch_size': self.settings.get('embeddings.batch_size', 32)
        }
        self.embedding_engine = EmbeddingEngine(**embedding_config)
        
        self.sentence_generator = SentenceGenerator()
        
        db_path = self.settings.get_database_path()
        self.storage = ExperimentStorage(db_path)
        
        self.executor = ExperimentExecutor(
            self.translation_chain,
            self.embedding_engine,
            self.storage
        )
        
        logger.info(f"Initialized ExperimentRunner with agent: {agent_type}")
    
    def run_single_experiment(
        self,
        sentence: str,
        error_rate: float
    ) -> Optional[int]:
        """
        Run single experiment: translation chain + analysis.
        
        Args:
            sentence: Original English sentence
            error_rate: Target error rate (0.0 to 1.0)
            
        Returns:
            Experiment ID if successful, None otherwise
        """
        return self.executor.execute_single(sentence, error_rate)
    
    def run_full_experiment_suite(
        self,
        num_sentences: Optional[int] = None,
        error_rates: Optional[List[float]] = None
    ) -> Dict[str, any]:
        """
        Run complete experiment suite across error rates and sentences.
        
        Args:
            num_sentences: Number of sentences to test (None for all)
            error_rates: List of error rates (None for config default)
            
        Returns:
            Dictionary with experiment results summary
        """
        if error_rates is None:
            error_rates = [r / 100.0 for r in self.settings.get_error_rates()]
        
        sentences = self.sentence_generator.get_sentences(num_sentences)
        
        logger.info(
            f"Starting full experiment suite: "
            f"{len(sentences)} sentences × {len(error_rates)} error rates = "
            f"{len(sentences) * len(error_rates)} experiments"
        )
        
        results = {
            'total_experiments': 0,
            'successful_experiments': 0,
            'failed_experiments': 0,
            'experiment_ids': []
        }
        
        for sentence in sentences:
            for error_rate in error_rates:
                results['total_experiments'] += 1
                
                experiment_id = self.run_single_experiment(sentence, error_rate)
                
                if experiment_id is not None:
                    results['successful_experiments'] += 1
                    results['experiment_ids'].append(experiment_id)
                else:
                    results['failed_experiments'] += 1
        
        results['success_rate'] = (
            results['successful_experiments'] / results['total_experiments']
            if results['total_experiments'] > 0 else 0
        )
        
        logger.info(
            f"Experiment suite completed: "
            f"{results['successful_experiments']}/{results['total_experiments']} successful "
            f"({results['success_rate']:.1%})"
        )
        
        return results
    
    def load_sentences_from_file(self, filepath: Path) -> None:
        """
        Load test sentences from file.
        
        Args:
            filepath: Path to sentences JSON file
        """
        self.sentence_generator.load_from_file(filepath)
        logger.info(f"Loaded {len(self.sentence_generator.sentences)} sentences from {filepath}")
    
    def save_sentences_to_file(self, filepath: Path) -> None:
        """
        Save current sentences to file.
        
        Args:
            filepath: Path to save sentences
        """
        self.sentence_generator.save_to_file(filepath)
        logger.info(f"Saved {len(self.sentence_generator.sentences)} sentences to {filepath}")

