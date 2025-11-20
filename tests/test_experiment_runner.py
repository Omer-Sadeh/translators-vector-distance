import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import numpy as np

from src.data.experiment_runner import ExperimentRunner
from src.data.experiment_executor import ExperimentExecutor
from src.translation.chain import ChainResult
from datetime import datetime


class TestExperimentExecutor:
    """Tests for ExperimentExecutor."""
    
    def test_initialization(self):
        """Test executor initialization."""
        mock_chain = Mock()
        mock_embedding = Mock()
        mock_storage = Mock()
        
        executor = ExperimentExecutor(
            translation_chain=mock_chain,
            embedding_engine=mock_embedding,
            storage=mock_storage
        )
        assert executor.translation_chain == mock_chain
        assert executor.embedding_engine == mock_embedding
        assert executor.storage == mock_storage
    
    def test_execute_single_success(self):
        """Test successful single experiment execution."""
        # Create mocks
        mock_chain = Mock()
        mock_embedding = Mock()
        mock_storage = Mock()
        
        # Mock chain result
        chain_result = ChainResult(
            original_text="Hello",
            corrupted_text="Hallo",
            error_rate_target=0.1,
            error_rate_actual=0.1,
            translation_fr="Bonjour",
            translation_he="שלום",
            translation_en="Hello",
            agent_type="test",
            total_duration_seconds=1.0,
            individual_durations={'en_to_fr': 0.3, 'fr_to_he': 0.3, 'he_to_en': 0.4},
            success=True,
            error_message=None,
            timestamp=datetime.now(),
            metadata={}
        )
        
        mock_chain.execute_chain = Mock(return_value=chain_result)
        mock_embedding.encode = Mock(return_value=np.array([0.1, 0.2, 0.3]))
        mock_storage.get_or_create_sentence = Mock(return_value=1)
        mock_storage.store_experiment = Mock(return_value=100)
        
        executor = ExperimentExecutor(mock_chain, mock_embedding, mock_storage)
        result_id = executor.execute_single("Hello", 0.1)
        
        assert result_id == 100
        mock_chain.execute_chain.assert_called_once_with("Hello", 0.1)
        assert mock_embedding.encode.call_count == 2
        mock_storage.store_experiment.assert_called_once()
    
    def test_execute_single_chain_failure(self):
        """Test single experiment with chain failure."""
        mock_chain = Mock()
        mock_embedding = Mock()
        mock_storage = Mock()
        
        chain_result = ChainResult(
            original_text="Hello",
            corrupted_text="Hello",
            error_rate_target=0.0,
            error_rate_actual=0.0,
            translation_fr="",
            translation_he="",
            translation_en="",
            agent_type="test",
            total_duration_seconds=0.5,
            individual_durations={},
            success=False,
            error_message="Translation failed",
            timestamp=datetime.now(),
            metadata={}
        )
        
        mock_chain.execute_chain = Mock(return_value=chain_result)
        
        executor = ExperimentExecutor(mock_chain, mock_embedding, mock_storage)
        result_id = executor.execute_single("Hello", 0.0)
        
        assert result_id is None
        mock_embedding.encode.assert_not_called()
        mock_storage.store_experiment.assert_not_called()
    
    def test_execute_single_exception(self):
        """Test single experiment with exception."""
        mock_chain = Mock()
        mock_embedding = Mock()
        mock_storage = Mock()
        
        mock_chain.execute_chain = Mock(side_effect=Exception("Test error"))
        
        executor = ExperimentExecutor(mock_chain, mock_embedding, mock_storage)
        result_id = executor.execute_single("Hello", 0.0)
        
        assert result_id is None


class TestExperimentRunner:
    """Tests for ExperimentRunner."""
    
    @patch('src.data.experiment_runner.ExperimentStorage')
    @patch('src.data.experiment_runner.EmbeddingEngine')
    @patch('src.data.experiment_runner.AgentFactory')
    @patch('src.data.experiment_runner.get_settings')
    def test_initialization(self, mock_settings, mock_factory, mock_embedding, mock_storage):
        """Test runner initialization."""
        mock_settings_obj = Mock()
        mock_settings_obj.get_agent_config = Mock(return_value={'timeout': 30})
        mock_settings_obj.get_embedding_model = Mock(return_value='test-model')
        mock_settings_obj.get = Mock(return_value='cpu')
        mock_settings_obj.get_database_path = Mock(return_value='test.db')
        mock_settings.return_value = mock_settings_obj
        
        mock_agent = Mock()
        mock_factory.create = Mock(return_value=mock_agent)
        
        runner = ExperimentRunner('test_agent')
        
        assert runner.agent_type == 'test_agent'
        mock_factory.create.assert_called_once()
    
    @patch('src.data.experiment_runner.ExperimentExecutor')
    @patch('src.data.experiment_runner.ExperimentStorage')
    @patch('src.data.experiment_runner.EmbeddingEngine')
    @patch('src.data.experiment_runner.AgentFactory')
    @patch('src.data.experiment_runner.get_settings')
    def test_run_single_experiment(
        self, mock_settings, mock_factory, mock_embedding, 
        mock_storage, mock_executor_class
    ):
        """Test running single experiment."""
        mock_settings_obj = Mock()
        mock_settings_obj.get_agent_config = Mock(return_value={})
        mock_settings_obj.get_embedding_model = Mock(return_value='model')
        mock_settings_obj.get = Mock(return_value='cpu')
        mock_settings_obj.get_database_path = Mock(return_value='test.db')
        mock_settings.return_value = mock_settings_obj
        
        mock_agent = Mock()
        mock_factory.create = Mock(return_value=mock_agent)
        
        mock_executor = Mock()
        mock_executor.execute_single = Mock(return_value=123)
        mock_executor_class.return_value = mock_executor
        
        runner = ExperimentRunner('test_agent')
        result_id = runner.run_single_experiment("Test sentence", 0.1)
        
        assert result_id == 123
        mock_executor.execute_single.assert_called_once_with("Test sentence", 0.1)
    
    @patch('src.data.experiment_runner.ExperimentExecutor')
    @patch('src.data.experiment_runner.SentenceGenerator')
    @patch('src.data.experiment_runner.ExperimentStorage')
    @patch('src.data.experiment_runner.EmbeddingEngine')
    @patch('src.data.experiment_runner.AgentFactory')
    @patch('src.data.experiment_runner.get_settings')
    def test_run_full_experiment_suite(
        self, mock_settings, mock_factory, mock_embedding,
        mock_storage, mock_generator_class, mock_executor_class
    ):
        """Test running full experiment suite."""
        mock_settings_obj = Mock()
        mock_settings_obj.get_agent_config = Mock(return_value={})
        mock_settings_obj.get_embedding_model = Mock(return_value='model')
        mock_settings_obj.get = Mock(return_value='cpu')
        mock_settings_obj.get_database_path = Mock(return_value='test.db')
        mock_settings_obj.get_error_rates = Mock(return_value=[0, 10, 25])
        mock_settings.return_value = mock_settings_obj
        
        mock_agent = Mock()
        mock_factory.create = Mock(return_value=mock_agent)
        
        mock_executor = Mock()
        mock_executor.execute_single = Mock(side_effect=[1, 2, None, 4, 5, 6])
        mock_executor_class.return_value = mock_executor
        
        runner = ExperimentRunner('test_agent')
        runner.sentence_generator = Mock()
        runner.sentence_generator.get_sentences = Mock(return_value=["S1", "S2"])
        
        results = runner.run_full_experiment_suite()
        
        assert results['total_experiments'] == 6
        assert results['successful_experiments'] == 5
        assert results['failed_experiments'] == 1
        assert results['success_rate'] == pytest.approx(5/6)
        assert len(results['experiment_ids']) == 5
    
    @patch('src.data.experiment_runner.ExperimentExecutor')
    @patch('src.data.experiment_runner.ExperimentStorage')
    @patch('src.data.experiment_runner.EmbeddingEngine')
    @patch('src.data.experiment_runner.AgentFactory')
    @patch('src.data.experiment_runner.get_settings')
    def test_load_sentences_from_file(
        self, mock_settings, mock_factory, mock_embedding,
        mock_storage, mock_executor_class
    ):
        """Test loading sentences from file."""
        mock_settings_obj = Mock()
        mock_settings_obj.get_agent_config = Mock(return_value={})
        mock_settings_obj.get_embedding_model = Mock(return_value='model')
        mock_settings_obj.get = Mock(return_value='cpu')
        mock_settings_obj.get_database_path = Mock(return_value='test.db')
        mock_settings.return_value = mock_settings_obj
        
        mock_agent = Mock()
        mock_factory.create = Mock(return_value=mock_agent)
        
        runner = ExperimentRunner('test_agent')
        runner.sentence_generator = Mock()
        runner.sentence_generator.load_from_file = Mock()
        runner.sentence_generator.sentences = ['S1', 'S2', 'S3']
        
        runner.load_sentences_from_file(Path("test.json"))
        
        runner.sentence_generator.load_from_file.assert_called_once()
    
    @patch('src.data.experiment_runner.ExperimentExecutor')
    @patch('src.data.experiment_runner.ExperimentStorage')
    @patch('src.data.experiment_runner.EmbeddingEngine')
    @patch('src.data.experiment_runner.AgentFactory')
    @patch('src.data.experiment_runner.get_settings')
    def test_save_sentences_to_file(
        self, mock_settings, mock_factory, mock_embedding,
        mock_storage, mock_executor_class
    ):
        """Test saving sentences to file."""
        mock_settings_obj = Mock()
        mock_settings_obj.get_agent_config = Mock(return_value={})
        mock_settings_obj.get_embedding_model = Mock(return_value='model')
        mock_settings_obj.get = Mock(return_value='cpu')
        mock_settings_obj.get_database_path = Mock(return_value='test.db')
        mock_settings.return_value = mock_settings_obj
        
        mock_agent = Mock()
        mock_factory.create = Mock(return_value=mock_agent)
        
        runner = ExperimentRunner('test_agent')
        runner.sentence_generator = Mock()
        runner.sentence_generator.save_to_file = Mock()
        runner.sentence_generator.sentences = ['S1', 'S2']
        
        runner.save_sentences_to_file(Path("output.json"))
        
        runner.sentence_generator.save_to_file.assert_called_once()

