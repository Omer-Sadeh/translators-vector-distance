import sqlite3
import json
import numpy as np
from pathlib import Path
from typing import Dict, Any

from src.translation.chain import ChainResult


class StorageMutations:
    """Insert/Update/Delete operations for ExperimentStorage."""
    
    def __init__(self, db_path: Path):
        """
        Initialize mutation handler.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
    
    def store_sentence(self, text: str) -> int:
        """Store a sentence and return its ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            word_count = len(text.split())
            
            cursor.execute("""
                INSERT INTO sentences (text, word_count)
                VALUES (?, ?)
            """, (text, word_count))
            
            conn.commit()
            return cursor.lastrowid
    
    def get_or_create_sentence(self, text: str) -> int:
        """Get existing sentence ID or create new one."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM sentences WHERE text = ?", (text,))
            row = cursor.fetchone()
            
            if row:
                return row[0]
            
            word_count = len(text.split())
            cursor.execute("""
                INSERT INTO sentences (text, word_count)
                VALUES (?, ?)
            """, (text, word_count))
            
            conn.commit()
            return cursor.lastrowid
    
    def store_experiment(
        self,
        sentence_id: int,
        chain_result: ChainResult,
        embeddings: Dict[str, np.ndarray],
        distances: Dict[str, float]
    ) -> int:
        """Store complete experiment with results."""
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
    
    def delete_experiment(self, experiment_id: int) -> None:
        """Delete an experiment and its embeddings."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM embeddings WHERE experiment_id = ?", (experiment_id,))
            cursor.execute("DELETE FROM experiments WHERE id = ?", (experiment_id,))
            conn.commit()
    
    def clear_all_data(self) -> None:
        """Clear all data from database (use with caution!)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM embeddings")
            cursor.execute("DELETE FROM experiments")
            cursor.execute("DELETE FROM sentences")
            conn.commit()

