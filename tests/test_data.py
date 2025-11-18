import pytest
import tempfile
from pathlib import Path
import json

from src.data.generator import SentenceGenerator
from src.data.storage import ExperimentStorage
from src.translation.chain import ChainResult
from datetime import datetime
import numpy as np


class TestSentenceGenerator:
    """Tests for SentenceGenerator."""
    
    def test_initialization(self):
        """Test generator initialization."""
        gen = SentenceGenerator()
        assert len(gen.sentences) > 0
    
    def test_get_sentences_all(self):
        """Test getting all sentences."""
        gen = SentenceGenerator()
        sentences = gen.get_sentences()
        assert len(sentences) == len(gen.DEFAULT_SENTENCES)
    
    def test_get_sentences_count(self):
        """Test getting specific count of sentences."""
        gen = SentenceGenerator()
        sentences = gen.get_sentences(count=5)
        assert len(sentences) == 5
    
    def test_add_sentence_valid(self):
        """Test adding valid sentence."""
        gen = SentenceGenerator()
        initial_count = len(gen.sentences)
        gen.add_sentence("This is a test sentence with more than fifteen words to meet the minimum requirement.")
        assert len(gen.sentences) == initial_count + 1
    
    def test_add_sentence_too_short(self):
        """Test adding sentence that's too short."""
        gen = SentenceGenerator()
        with pytest.raises(ValueError, match="at least 15 words"):
            gen.add_sentence("Short sentence")
    
    def test_validate_sentence(self):
        """Test sentence validation."""
        gen = SentenceGenerator()
        
        # Valid sentence (15+ words)
        result = gen.validate_sentence("This is a long enough sentence with more than fifteen words included here for testing validation.")
        assert result['valid'] is True
        assert result['word_count'] >= 15
        
        # Invalid sentence
        result = gen.validate_sentence("Too short")
        assert result['valid'] is False
    
    def test_save_and_load(self):
        """Test saving and loading sentences."""
        gen = SentenceGenerator()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test_sentences.json"
            
            # Save
            gen.save_to_file(filepath)
            assert filepath.exists()
            
            # Load
            gen2 = SentenceGenerator()
            gen2.load_from_file(filepath)
            assert len(gen2.sentences) == len(gen.sentences)
    
    def test_get_statistics(self):
        """Test getting sentence statistics."""
        gen = SentenceGenerator()
        stats = gen.get_statistics()
        
        assert 'total_sentences' in stats
        assert 'word_count' in stats
        assert 'char_count' in stats
        assert stats['total_sentences'] > 0


class TestExperimentStorage:
    """Tests for ExperimentStorage."""
    
    def test_initialization(self):
        """Test storage initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            storage = ExperimentStorage(db_path)
            assert db_path.exists()
    
    def test_store_sentence(self):
        """Test storing a sentence."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            storage = ExperimentStorage(db_path)
            
            sentence_id = storage.store_sentence("Test sentence")
            assert sentence_id > 0
    
    def test_get_or_create_sentence_new(self):
        """Test getting/creating new sentence."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            storage = ExperimentStorage(db_path)
            
            sentence_id = storage.get_or_create_sentence("New sentence")
            assert sentence_id > 0
    
    def test_get_or_create_sentence_existing(self):
        """Test getting existing sentence."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            storage = ExperimentStorage(db_path)
            
            text = "Existing sentence"
            id1 = storage.get_or_create_sentence(text)
            id2 = storage.get_or_create_sentence(text)
            
            assert id1 == id2
    
    def test_store_experiment(self):
        """Test storing complete experiment."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            storage = ExperimentStorage(db_path)
            
            sentence_id = storage.store_sentence("Test sentence")
            
            chain_result = ChainResult(
                original_text="Test",
                corrupted_text="Tets",
                error_rate_target=0.25,
                error_rate_actual=0.25,
                translation_fr="Fr",
                translation_he="He",
                translation_en="En",
                agent_type="test",
                total_duration_seconds=10.0,
                individual_durations={'en_to_fr': 3.0, 'fr_to_he': 3.0, 'he_to_en': 4.0},
                success=True,
                error_message=None,
                timestamp=datetime.now(),
                metadata={}
            )
            
            embeddings = {
                'original': np.array([0.1, 0.2, 0.3]),
                'final': np.array([0.2, 0.3, 0.4])
            }
            
            distances = {
                'cosine': 0.1,
                'euclidean': 0.2,
                'manhattan': 0.3
            }
            
            exp_id = storage.store_experiment(sentence_id, chain_result, embeddings, distances)
            assert exp_id > 0
    
    def test_get_all_results(self):
        """Test getting all results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            storage = ExperimentStorage(db_path)
            
            results = storage.get_all_results()
            assert isinstance(results, list)
    
    def test_get_statistics(self):
        """Test getting database statistics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            storage = ExperimentStorage(db_path)
            
            stats = storage.get_statistics()
            assert 'total_sentences' in stats
            assert 'total_experiments' in stats
            assert 'success_rate' in stats

