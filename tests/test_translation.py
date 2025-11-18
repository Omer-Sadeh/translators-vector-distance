import pytest
from unittest.mock import Mock, MagicMock

from src.translation.error_injector import ErrorInjector
from src.translation.chain import TranslationChain, ChainResult
from src.agents.base import BaseAgent, TranslationResult
from datetime import datetime


class TestErrorInjector:
    """Tests for ErrorInjector."""
    
    def test_initialization(self):
        """Test error injector initialization."""
        injector = ErrorInjector(seed=42)
        assert injector is not None
    
    def test_inject_errors_zero_rate(self):
        """Test error injection with 0% rate."""
        injector = ErrorInjector(seed=42)
        text = "The quick brown fox jumps"
        result = injector.inject_errors(text, 0.0)
        assert result == text
    
    def test_inject_errors_nonzero_rate(self):
        """Test error injection with non-zero rate."""
        injector = ErrorInjector(seed=42)
        text = "The quick brown fox jumps over the lazy dog"
        result = injector.inject_errors(text, 0.5)
        assert result != text
        assert len(result.split()) == len(text.split())
    
    def test_inject_errors_invalid_rate(self):
        """Test error injection with invalid rate."""
        injector = ErrorInjector()
        with pytest.raises(ValueError, match="Error rate must be between 0 and 1"):
            injector.inject_errors("Hello", 1.5)
        with pytest.raises(ValueError, match="Error rate must be between 0 and 1"):
            injector.inject_errors("Hello", -0.1)
    
    def test_calculate_actual_error_rate(self):
        """Test actual error rate calculation."""
        injector = ErrorInjector()
        original = "The quick brown fox"
        corrupted = "The quikc brown fox"
        
        rate = injector.calculate_actual_error_rate(original, corrupted)
        assert 0.0 <= rate <= 1.0
        assert rate == 0.25  # 1 out of 4 words changed
    
    def test_calculate_error_rate_identical(self):
        """Test error rate for identical texts."""
        injector = ErrorInjector()
        text = "Hello world"
        rate = injector.calculate_actual_error_rate(text, text)
        assert rate == 0.0
    
    def test_maintain_punctuation(self):
        """Test that punctuation is maintained."""
        injector = ErrorInjector(seed=42)
        text = "Hello, world! How are you?"
        result = injector.inject_errors(text, 0.5, maintain_punctuation=True)
        assert ',' in result
        assert '!' in result
        assert '?' in result
    
    def test_character_operations(self):
        """Test individual character operations."""
        injector = ErrorInjector(seed=42)
        
        # Test swap
        result = injector._character_swap("hello")
        assert len(result) == len("hello")
        
        # Test deletion
        result = injector._character_deletion("hello")
        assert len(result) == len("hello") - 1
        
        # Test insertion
        result = injector._character_insertion("hello")
        assert len(result) == len("hello") + 1
        
        # Test substitution
        result = injector._character_substitution("hello")
        assert len(result) == len("hello")


class TestTranslationChain:
    """Tests for TranslationChain."""
    
    def create_mock_agent(self):
        """Create a mock agent for testing."""
        agent = Mock(spec=BaseAgent)
        agent.get_agent_type.return_value = 'mock'
        return agent
    
    def test_initialization(self):
        """Test chain initialization."""
        agent = self.create_mock_agent()
        chain = TranslationChain(agent)
        assert chain.agent == agent
        assert chain.error_injector is not None
    
    def test_initialization_with_injector(self):
        """Test chain initialization with custom injector."""
        agent = self.create_mock_agent()
        injector = ErrorInjector(seed=42)
        chain = TranslationChain(agent, injector)
        assert chain.error_injector == injector
    
    def test_execute_chain_empty_text(self):
        """Test chain execution with empty text."""
        agent = self.create_mock_agent()
        chain = TranslationChain(agent)
        
        with pytest.raises(ValueError, match="Text cannot be empty"):
            chain.execute_chain("", 0.0)
    
    def test_execute_chain_invalid_error_rate(self):
        """Test chain execution with invalid error rate."""
        agent = self.create_mock_agent()
        chain = TranslationChain(agent)
        
        with pytest.raises(ValueError, match="Error rate must be between 0 and 1"):
            chain.execute_chain("Hello", 1.5)
    
    def test_execute_chain_success(self):
        """Test successful chain execution."""
        agent = self.create_mock_agent()
        
        # Mock translate method to return results for each step
        def mock_translate(text, source, target):
            return TranslationResult(
                translated_text=f"Translated_{text}",
                source_language=source,
                target_language=target,
                agent_type='mock',
                duration_seconds=1.0,
                metadata={},
                timestamp=datetime.now()
            )
        
        agent.translate = Mock(side_effect=mock_translate)
        
        chain = TranslationChain(agent)
        result = chain.execute_chain("Hello world", 0.0)
        
        assert isinstance(result, ChainResult)
        assert result.success is True
        assert result.agent_type == 'mock'
        assert result.error_rate_target == 0.0
        assert agent.translate.call_count == 3  # EN→FR, FR→HE, HE→EN
    
    def test_execute_chain_failure(self):
        """Test chain execution with failure."""
        agent = self.create_mock_agent()
        agent.translate = Mock(side_effect=RuntimeError("Translation failed"))
        
        chain = TranslationChain(agent)
        result = chain.execute_chain("Hello world", 0.0)
        
        assert isinstance(result, ChainResult)
        assert result.success is False
        assert "Translation failed" in result.error_message
    
    def test_get_intermediate_translations(self):
        """Test getting intermediate translations."""
        agent = self.create_mock_agent()
        
        def mock_translate(text, source, target):
            return TranslationResult(
                translated_text=f"{target}_translation",
                source_language=source,
                target_language=target,
                agent_type='mock',
                duration_seconds=1.0,
                metadata={},
                timestamp=datetime.now()
            )
        
        agent.translate = Mock(side_effect=mock_translate)
        
        chain = TranslationChain(agent)
        chain.execute_chain("Hello world", 0.0)
        
        intermediates = chain.get_intermediate_translations()
        assert len(intermediates) == 3
        assert all(isinstance(r, TranslationResult) for r in intermediates)

