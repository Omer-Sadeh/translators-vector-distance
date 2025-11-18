import sqlite3
import numpy as np
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime

from src.translation.chain import ChainResult


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
                    FOREIGN KEY (experiment_id) REFERENCES experiments(id)
                )
            """)
            
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_experiments_agent ON experiments(agent_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_experiments_error_rate ON experiments(error_rate_target)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_experiments_sentence ON experiments(sentence_id)")
            
            conn.commit()
    
    def store_sentence(self, text: str) -> int:
        """
        Store a sentence and return its ID.
        
        Args:
            text: Sentence text
            
        Returns:
            Sentence ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO sentences (text, word_count) VALUES (?, ?)",
                (text, len(text.split()))
            )
            conn.commit()
            return cursor.lastrowid
    
    def get_or_create_sentence(self, text: str) -> int:
        """
        Get existing sentence ID or create new one.
        
        Args:
            text: Sentence text
            
        Returns:
            Sentence ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM sentences WHERE text = ?", (text,))
            result = cursor.fetchone()
            
            if result:
                return result[0]
            else:
                return self.store_sentence(text)
    
    def store_experiment(
        self,
        sentence_id: int,
        chain_result: ChainResult,
        embeddings: Dict[str, np.ndarray],
        distances: Dict[str, float]
    ) -> int:
        """
        Store complete experiment results.
        
        Args:
            sentence_id: ID of original sentence
            chain_result: Translation chain results
            embeddings: Dictionary with 'original' and 'final' embeddings
            distances: Dictionary with distance metrics
            
        Returns:
            Experiment ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            metadata_json = json.dumps(chain_result.metadata)
            
            cursor.execute("""
                INSERT INTO experiments (
                    sentence_id, agent_type, error_rate_target, error_rate_actual,
                    corrupted_text, translation_fr, translation_he, translation_en,
                    duration_seconds, duration_en_fr, duration_fr_he, duration_he_en,
                    success, error_message, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                sentence_id,
                chain_result.agent_type,
                chain_result.error_rate_target,
                chain_result.error_rate_actual,
                chain_result.corrupted_text,
                chain_result.translation_fr,
                chain_result.translation_he,
                chain_result.translation_en,
                chain_result.total_duration_seconds,
                chain_result.individual_durations.get('en_to_fr', 0.0),
                chain_result.individual_durations.get('fr_to_he', 0.0),
                chain_result.individual_durations.get('he_to_en', 0.0),
                chain_result.success,
                chain_result.error_message,
                metadata_json
            ))
            
            experiment_id = cursor.lastrowid
            
            original_emb_blob = embeddings['original'].tobytes()
            final_emb_blob = embeddings['final'].tobytes()
            
            cursor.execute("""
                INSERT INTO embeddings (
                    experiment_id, original_embedding, final_embedding,
                    cosine_distance, euclidean_distance, manhattan_distance
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                experiment_id,
                original_emb_blob,
                final_emb_blob,
                distances['cosine'],
                distances['euclidean'],
                distances['manhattan']
            ))
            
            conn.commit()
            return experiment_id
    
    def get_all_results(self) -> List[Dict[str, Any]]:
        """
        Get all experiment results.
        
        Returns:
            List of experiment dictionaries
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    e.*,
                    s.text as original_text,
                    emb.cosine_distance,
                    emb.euclidean_distance,
                    emb.manhattan_distance
                FROM experiments e
                JOIN sentences s ON e.sentence_id = s.id
                LEFT JOIN embeddings emb ON e.id = emb.experiment_id
                ORDER BY e.created_at DESC
            """)
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_results_by_agent(self, agent_type: str) -> List[Dict[str, Any]]:
        """
        Get results filtered by agent type.
        
        Args:
            agent_type: Agent type to filter
            
        Returns:
            List of experiment dictionaries
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    e.*,
                    s.text as original_text,
                    emb.cosine_distance,
                    emb.euclidean_distance,
                    emb.manhattan_distance
                FROM experiments e
                JOIN sentences s ON e.sentence_id = s.id
                LEFT JOIN embeddings emb ON e.id = emb.experiment_id
                WHERE e.agent_type = ?
                ORDER BY e.error_rate_target, e.created_at
            """, (agent_type,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_results_by_error_rate(self, error_rate: float) -> List[Dict[str, Any]]:
        """
        Get results filtered by error rate.
        
        Args:
            error_rate: Error rate to filter
            
        Returns:
            List of experiment dictionaries
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    e.*,
                    s.text as original_text,
                    emb.cosine_distance,
                    emb.euclidean_distance,
                    emb.manhattan_distance
                FROM experiments e
                JOIN sentences s ON e.sentence_id = s.id
                LEFT JOIN embeddings emb ON e.id = emb.experiment_id
                WHERE ABS(e.error_rate_target - ?) < 0.01
                ORDER BY e.agent_type, e.created_at
            """, (error_rate,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Dictionary with statistics
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM sentences")
            sentence_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM experiments")
            experiment_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM experiments WHERE success = 1")
            successful_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT DISTINCT agent_type FROM experiments")
            agents = [row[0] for row in cursor.fetchall()]
            
            cursor.execute("SELECT DISTINCT error_rate_target FROM experiments ORDER BY error_rate_target")
            error_rates = [row[0] for row in cursor.fetchall()]
            
            return {
                'total_sentences': sentence_count,
                'total_experiments': experiment_count,
                'successful_experiments': successful_count,
                'success_rate': successful_count / experiment_count if experiment_count > 0 else 0,
                'agents': agents,
                'error_rates': error_rates
            }
    
    def clear_all_data(self) -> None:
        """Clear all data from database (use with caution!)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM embeddings")
            cursor.execute("DELETE FROM experiments")
            cursor.execute("DELETE FROM sentences")
            conn.commit()

