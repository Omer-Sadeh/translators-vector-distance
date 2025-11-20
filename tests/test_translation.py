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
    
    def test_inject_errors_100_percent(self):
        """Test error injection with 100% rate."""
        injector = ErrorInjector(seed=42)
        text = "The quick brown fox jumps"
        result = injector.inject_errors(text, 1.0)
        
        # All words should be corrupted
        assert result != text
        assert len(result.split()) == len(text.split())
    
    def test_split_punctuation_leading(self):
        """Test splitting word with leading punctuation."""
        injector = ErrorInjector()
        leading, core, trailing = injector._split_punctuation("'hello")
        
        assert leading == "'"
        assert core == "hello"
        assert trailing == ""
    
    def test_split_punctuation_trailing(self):
        """Test splitting word with trailing punctuation."""
        injector = ErrorInjector()
        leading, core, trailing = injector._split_punctuation("hello!")
        
        assert leading == ""
        assert core == "hello"
        assert trailing == "!"
    
    def test_split_punctuation_both(self):
        """Test splitting word with both leading and trailing."""
        injector = ErrorInjector()
        leading, core, trailing = injector._split_punctuation("'hello,'")
        
        assert leading == "'"
        assert core == "hello"
        assert trailing == ",'"
    
    def test_split_punctuation_none(self):
        """Test splitting word with no punctuation."""
        injector = ErrorInjector()
        leading, core, trailing = injector._split_punctuation("hello")
        
        assert leading == ""
        assert core == "hello"
        assert trailing == ""
    
    def test_corrupt_word_short(self):
        """Test corrupting very short word."""
        injector = ErrorInjector(seed=42)
        result = injector._corrupt_word("a", True, True)
        
        # Single character words should not be corrupted
        assert result == "a"
    
    def test_corrupt_word_with_capitalization(self):
        """Test corruption preserves capitalization."""
        injector = ErrorInjector(seed=42)
        result = injector._corrupt_word("Hello", False, True)
        
        # Should be different but still capitalized
        if result != "Hello":
            assert result[0].isupper()
    
    def test_character_swap_short_word(self):
        """Test swap on 2-character word."""
        injector = ErrorInjector(seed=42)
        result = injector._character_swap("ab")
        
        assert len(result) == 2
        assert result == "ba"
    
    def test_character_deletion_minimum(self):
        """Test deletion on 2-character word."""
        injector = ErrorInjector(seed=42)
        result = injector._character_deletion("ab")
        
        assert len(result) == 1
        assert result in ["a", "b"]
    
    def test_character_insertion_beginning(self):
        """Test character insertion at beginning."""
        injector = ErrorInjector(seed=0)
        result = injector._character_insertion("test")
        
        assert len(result) == 5
    
    def test_character_substitution_keyboard_neighbors(self):
        """Test substitution uses keyboard neighbors."""
        injector = ErrorInjector(seed=42)
        result = injector._character_substitution("hello")
        
        assert len(result) == 5
        assert result != "hello"
    
    def test_character_substitution_non_alpha(self):
        """Test substitution on non-alphabetic character."""
        injector = ErrorInjector(seed=42)
        result = injector._character_substitution("123")
        
        # Non-alpha chars should be replaced with random letter
        assert len(result) == 3
    
    def test_calculate_error_rate_all_different(self):
        """Test error rate with all words different."""
        injector = ErrorInjector()
        original = "the quick brown"
        corrupted = "abc def ghi"
        
        rate = injector.calculate_actual_error_rate(original, corrupted)
        assert rate == 1.0
    
    def test_calculate_error_rate_half_different(self):
        """Test error rate with half different."""
        injector = ErrorInjector()
        original = "the quick brown fox"
        corrupted = "the quick abc def"
        
        rate = injector.calculate_actual_error_rate(original, corrupted)
        assert rate == 0.5
    
    def test_calculate_error_rate_empty(self):
        """Test error rate with empty strings."""
        injector = ErrorInjector()
        rate = injector.calculate_actual_error_rate("", "")
        
        assert rate == 0.0
    
    def test_calculate_error_rate_different_lengths(self):
        """Test error rate with different length texts."""
        injector = ErrorInjector()
        original = "the quick brown"
        corrupted = "the quick"
        
        rate = injector.calculate_actual_error_rate(original, corrupted)
        assert 0.0 <= rate <= 1.0
    
    def test_inject_errors_no_capitalization_preservation(self):
        """Test error injection without capitalization preservation."""
        injector = ErrorInjector(seed=42)
        text = "Hello World"
        result = injector.inject_errors(text, 0.5, maintain_capitalization=False)
        
        assert len(result.split()) == 2
    
    def test_inject_errors_reproducible(self):
        """Test error injection is reproducible with same seed."""
        text = "The quick brown fox jumps"
        
        injector1 = ErrorInjector(seed=42)
        result1 = injector1.inject_errors(text, 0.5)
        
        injector2 = ErrorInjector(seed=42)
        result2 = injector2.inject_errors(text, 0.5)
        
        assert result1 == result2
    
    def test_inject_errors_single_word(self):
        """Test error injection on single word."""
        injector = ErrorInjector(seed=42)
        text = "hello"
        result = injector.inject_errors(text, 1.0)
        
        # Single word with 100% rate should be corrupted, but result may vary
        # Just check it's still a single word
        assert len(result.split()) == 1
        # Note: corruption may or may not change the word depending on random seed
    
    def test_keyboard_neighbors_coverage(self):
        """Test keyboard neighbors mapping has all lowercase letters."""
        injector = ErrorInjector()
        
        for letter in 'abcdefghijklmnopqrstuvwxyz':
            assert letter in injector.keyboard_neighbors
            assert len(injector.keyboard_neighbors[letter]) > 0


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

