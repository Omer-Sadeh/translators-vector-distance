import sqlite3
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Any

from src.translation.chain import ChainResult
from src.data.storage_queries import StorageQueries
from src.data.storage_mutations import StorageMutations


class ExperimentStorage:
    """
    SQLite database storage for experiment results.
    
    Manages persistent storage of sentences, experiments, embeddings,
    and distance metrics.
    """
    
    def __init__(self, db_path: Path):
        """
        Initialize storage.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        
        self.queries = StorageQueries(self.db_path)
        self.mutations = StorageMutations(self.db_path)
    
    def _init_database(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sentences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    word_count INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS experiments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sentence_id INTEGER NOT NULL,
                    agent_type TEXT NOT NULL,
                    error_rate_target REAL NOT NULL,
                    error_rate_actual REAL NOT NULL,
                    corrupted_text TEXT NOT NULL,
                    translation_fr TEXT,
                    translation_he TEXT,
                    translation_en TEXT,
                    duration_seconds REAL,
                    duration_en_fr REAL,
                    duration_fr_he REAL,
                    duration_he_en REAL,
                    success BOOLEAN NOT NULL,
                    error_message TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (sentence_id) REFERENCES sentences(id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS embeddings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    experiment_id INTEGER NOT NULL,
                    original_embedding BLOB NOT NULL,
                    final_embedding BLOB NOT NULL,
                    cosine_distance REAL NOT NULL,
                    euclidean_distance REAL NOT NULL,
                    manhattan_distance REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (experiment_id) REFERENCES experiments(id)
                )
            """)
            
            conn.commit()
    
    def store_sentence(self, text: str) -> int:
        """Store a sentence and return its ID."""
        return self.mutations.store_sentence(text)
    
    def get_or_create_sentence(self, text: str) -> int:
        """Get existing sentence ID or create new one."""
        return self.mutations.get_or_create_sentence(text)
    
    def store_experiment(
        self,
        sentence_id: int,
        chain_result: ChainResult,
        embeddings: Dict[str, np.ndarray],
        distances: Dict[str, float]
    ) -> int:
        """Store complete experiment with results."""
        return self.mutations.store_experiment(
            sentence_id, chain_result, embeddings, distances
        )
    
    def get_all_results(self) -> List[Dict[str, Any]]:
        """Get all experiment results."""
        return self.queries.get_all_results()
    
    def get_results_by_agent(self, agent_type: str) -> List[Dict[str, Any]]:
        """Get results filtered by agent type."""
        return self.queries.get_results_by_agent(agent_type)
    
    def get_results_by_error_rate(self, error_rate: float) -> List[Dict[str, Any]]:
        """Get results filtered by error rate."""
        return self.queries.get_results_by_error_rate(error_rate)
    
    def query_results(
        self,
        agent_type: str = None,
        error_rate: float = None,
        success_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Query results with multiple filters."""
        return self.queries.query_results(agent_type, error_rate, success_only)
    
    def get_experiment_embeddings(self, experiment_id: int) -> Dict[str, np.ndarray]:
        """Get embedding vectors for an experiment."""
        return self.queries.get_experiment_embeddings(experiment_id)
    
    def count_experiments_by_agent(self) -> Dict[str, int]:
        """Count experiments grouped by agent type."""
        return self.queries.count_experiments_by_agent()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        return self.queries.get_statistics()
    
    def delete_experiment(self, experiment_id: int) -> None:
        """Delete an experiment and its embeddings."""
        self.mutations.delete_experiment(experiment_id)
    
    def clear_all_data(self) -> None:
        """Clear all data from database (use with caution!)."""
        self.mutations.clear_all_data()
