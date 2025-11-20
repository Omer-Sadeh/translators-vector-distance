import sqlite3
from pathlib import Path
from typing import List, Dict, Any
import numpy as np


class StorageQueries:
    """Query operations for ExperimentStorage."""
    
    def __init__(self, db_path: Path):
        """
        Initialize query handler.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
    
    def get_all_results(self) -> List[Dict[str, Any]]:
        """Get all experiment results."""
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
        """Get results filtered by agent type."""
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
        """Get results filtered by error rate."""
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
    
    def query_results(
        self,
        agent_type: str = None,
        error_rate: float = None,
        success_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Query results with multiple filters."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    e.*,
                    s.text as original_text,
                    emb.cosine_distance,
                    emb.euclidean_distance,
                    emb.manhattan_distance
                FROM experiments e
                JOIN sentences s ON e.sentence_id = s.id
                LEFT JOIN embeddings emb ON e.id = emb.experiment_id
                WHERE 1=1
            """
            params = []
            
            if agent_type:
                query += " AND e.agent_type = ?"
                params.append(agent_type)
            
            if error_rate is not None:
                query += " AND ABS(e.error_rate_target - ?) < 0.01"
                params.append(error_rate)
            
            if success_only:
                query += " AND e.success = 1"
            
            query += " ORDER BY e.created_at DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_experiment_embeddings(self, experiment_id: int) -> Dict[str, np.ndarray]:
        """Get embedding vectors for an experiment."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT original_embedding, final_embedding
                FROM embeddings
                WHERE experiment_id = ?
            """, (experiment_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            original_blob, final_blob = row
            
            return {
                'original': np.frombuffer(original_blob, dtype=np.float64),
                'final': np.frombuffer(final_blob, dtype=np.float64)
            }
    
    def count_experiments_by_agent(self) -> Dict[str, int]:
        """Count experiments grouped by agent type."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT agent_type, COUNT(*) as count
                FROM experiments
                GROUP BY agent_type
            """)
            
            return {row[0]: row[1] for row in cursor.fetchall()}
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
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

