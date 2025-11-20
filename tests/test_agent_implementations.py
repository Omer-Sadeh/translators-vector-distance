"""Tests for agent implementations with low coverage (gemini, claude, ollama)."""
import pytest
from unittest.mock import Mock, patch
import subprocess

from src.agents.gemini_agent import GeminiAgent
from src.agents.claude_agent import ClaudeAgent
from src.agents.ollama_agent import OllamaAgent
from src.agents.base import TranslationResult


class TestGeminiAgent:
    """Tests for GeminiAgent."""
    
    def test_initialization(self):
        """Test gemini agent initialization."""
        agent = GeminiAgent()
        assert agent.get_agent_type() == 'gemini'
        assert agent.command == 'gemini'
    
    def test_initialization_with_config(self):
        """Test initialization with custom config."""
        config = {'timeout': 60, 'retry_attempts': 5}
        agent = GeminiAgent(config)
        assert agent.timeout == 60
        assert agent.retry_attempts == 5
    
    @patch('src.agents.gemini_agent.subprocess.run')
    def test_translate_success(self, mock_run):
        """Test successful translation."""
        mock_run.return_value = Mock(
            stdout="Bonjour le monde",
            stderr="",
            returncode=0
        )
        
        agent = GeminiAgent({'retry_attempts': 1})
        result = agent.translate("Hello world", "en", "fr")
        
        assert isinstance(result, TranslationResult)
        assert result.translated_text == "Bonjour le monde"
        assert result.agent_type == "gemini"
    
    @patch('src.agents.gemini_agent.subprocess.run')
    def test_translate_timeout(self, mock_run):
        """Test translation timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired('cmd', 30)
        
        agent = GeminiAgent({'retry_attempts': 1, 'retry_delay': 0})
        
        with pytest.raises(RuntimeError, match="Translation timeout"):
            agent.translate("Hello", "en", "fr")
    
    @patch('src.agents.gemini_agent.subprocess.run')
    def test_translate_command_not_found(self, mock_run):
        """Test translation when command not found."""
        mock_run.side_effect = FileNotFoundError()
        
        agent = GeminiAgent()
        
        with pytest.raises(RuntimeError, match="Gemini CLI not found"):
            agent.translate("Hello", "en", "fr")
    
    @patch('src.agents.gemini_agent.subprocess.run')
    def test_translate_empty_output(self, mock_run):
        """Test translation with empty output."""
        mock_run.return_value = Mock(stdout="", stderr="", returncode=0)
        
        agent = GeminiAgent({'retry_attempts': 1})
        
        with pytest.raises(RuntimeError, match="Empty translation received"):
            agent.translate("Hello", "en", "fr")
    
    @patch('src.agents.gemini_agent.subprocess.run')
    def test_translate_with_retry(self, mock_run):
        """Test translation with retry logic."""
        # First attempt fails, second succeeds
        mock_run.side_effect = [
            Mock(stdout="", stderr="error", returncode=1),
            Mock(stdout="Bonjour", stderr="", returncode=0)
        ]
        
        agent = GeminiAgent({'retry_attempts': 2, 'retry_delay': 0})
        result = agent.translate("Hello", "en", "fr")
        
        assert result.translated_text == "Bonjour"
        assert mock_run.call_count == 2


class TestClaudeAgent:
    """Tests for ClaudeAgent."""
    
    def test_initialization(self):
        """Test claude agent initialization."""
        agent = ClaudeAgent()
        assert agent.get_agent_type() == 'claude'
        assert agent.command == 'claude'
    
    def test_initialization_with_config(self):
        """Test initialization with custom config."""
        config = {'timeout': 60, 'retry_attempts': 5}
        agent = ClaudeAgent(config)
        assert agent.timeout == 60
        assert agent.retry_attempts == 5
    
    @patch('src.agents.claude_agent.subprocess.run')
    def test_translate_success(self, mock_run):
        """Test successful translation."""
        mock_run.return_value = Mock(
            stdout="Bonjour le monde",
            stderr="",
            returncode=0
        )
        
        agent = ClaudeAgent({'retry_attempts': 1})
        result = agent.translate("Hello world", "en", "fr")
        
        assert isinstance(result, TranslationResult)
        assert result.translated_text == "Bonjour le monde"
        assert result.agent_type == "claude"
    
    @patch('src.agents.claude_agent.subprocess.run')
    def test_translate_timeout(self, mock_run):
        """Test translation timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired('cmd', 30)
        
        agent = ClaudeAgent({'retry_attempts': 1, 'retry_delay': 0})
        
        with pytest.raises(RuntimeError, match="Translation timeout"):
            agent.translate("Hello", "en", "fr")
    
    @patch('src.agents.claude_agent.subprocess.run')
    def test_translate_command_not_found(self, mock_run):
        """Test translation when command not found."""
        mock_run.side_effect = FileNotFoundError()
        
        agent = ClaudeAgent()
        
        with pytest.raises(RuntimeError, match="Claude CLI not found"):
            agent.translate("Hello", "en", "fr")
    
    @patch('src.agents.claude_agent.subprocess.run')
    def test_translate_empty_output(self, mock_run):
        """Test translation with empty output."""
        mock_run.return_value = Mock(stdout="", stderr="", returncode=0)
        
        agent = ClaudeAgent({'retry_attempts': 1})
        
        with pytest.raises(RuntimeError, match="Empty translation received"):
            agent.translate("Hello", "en", "fr")


class TestOllamaAgent:
    """Tests for OllamaAgent."""
    
    def test_initialization(self):
        """Test ollama agent initialization."""
        agent = OllamaAgent()
        assert agent.get_agent_type() == 'ollama'
        assert agent.command == 'ollama'
    
    def test_initialization_with_config(self):
        """Test initialization with custom config."""
        config = {'timeout': 60, 'retry_attempts': 5}
        agent = OllamaAgent(config)
        assert agent.timeout == 60
        assert agent.retry_attempts == 5
    
    @patch('src.agents.ollama_agent.subprocess.run')
    def test_translate_success(self, mock_run):
        """Test successful translation."""
        mock_run.return_value = Mock(
            stdout="Bonjour le monde",
            stderr="",
            returncode=0
        )
        
        agent = OllamaAgent({'retry_attempts': 1})
        result = agent.translate("Hello world", "en", "fr")
        
        assert isinstance(result, TranslationResult)
        assert result.translated_text == "Bonjour le monde"
        assert result.agent_type == "ollama"
    
    @patch('src.agents.ollama_agent.subprocess.run')
    def test_translate_timeout(self, mock_run):
        """Test translation timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired('cmd', 30)
        
        agent = OllamaAgent({'retry_attempts': 1, 'retry_delay': 0})
        
        with pytest.raises(RuntimeError, match="Translation timeout"):
            agent.translate("Hello", "en", "fr")
    
    @patch('src.agents.ollama_agent.subprocess.run')
    def test_translate_command_not_found(self, mock_run):
        """Test translation when command not found."""
        mock_run.side_effect = FileNotFoundError()
        
        agent = OllamaAgent()
        
        with pytest.raises(RuntimeError, match="Ollama not found"):
            agent.translate("Hello", "en", "fr")
    
    @patch('src.agents.ollama_agent.subprocess.run')
    def test_translate_empty_output(self, mock_run):
        """Test translation with empty output."""
        mock_run.return_value = Mock(stdout="", stderr="", returncode=0)
        
        agent = OllamaAgent({'retry_attempts': 1})
        
        with pytest.raises(RuntimeError, match="Empty translation received"):
            agent.translate("Hello", "en", "fr")
    
    @patch('src.agents.ollama_agent.subprocess.run')
    def test_translate_nonzero_return_code(self, mock_run):
        """Test translation with nonzero return code."""
        mock_run.return_value = Mock(
            stdout="",
            stderr="Error message",
            returncode=1
        )
        
        agent = OllamaAgent({'retry_attempts': 1})
        
        with pytest.raises(RuntimeError):
            agent.translate("Hello", "en", "fr")

