import pytest
from unittest.mock import Mock, patch, MagicMock
import subprocess

from src.agents.base import BaseAgent, TranslationResult
from src.agents.cursor_agent import CursorAgent
from src.agents.gemini_agent import GeminiAgent
from src.agents.claude_agent import ClaudeAgent
from src.agents.ollama_agent import OllamaAgent
from src.agents.factory import AgentFactory


class TestBaseAgent:
    """Tests for BaseAgent abstract class."""
    
    def test_validate_input_valid(self):
        """Test input validation with valid inputs."""
        agent = CursorAgent()
        agent.validate_input("Hello world", "en", "fr")
    
    def test_validate_input_empty_text(self):
        """Test input validation with empty text."""
        agent = CursorAgent()
        with pytest.raises(ValueError, match="Text cannot be empty"):
            agent.validate_input("", "en", "fr")
    
    def test_validate_input_invalid_source_lang(self):
        """Test input validation with invalid source language."""
        agent = CursorAgent()
        with pytest.raises(ValueError, match="Invalid source language"):
            agent.validate_input("Hello", "xx", "fr")
    
    def test_validate_input_same_languages(self):
        """Test input validation with same source and target."""
        agent = CursorAgent()
        with pytest.raises(ValueError, match="Source and target languages must be different"):
            agent.validate_input("Hello", "en", "en")


class TestCursorAgent:
    """Tests for CursorAgent."""
    
    def test_initialization(self):
        """Test agent initialization."""
        agent = CursorAgent()
        assert agent.get_agent_type() == 'cursor'
        assert agent.command == 'cursor-agent'
    
    def test_initialization_with_config(self):
        """Test agent initialization with custom config."""
        config = {'timeout': 60, 'retry_attempts': 5}
        agent = CursorAgent(config)
        assert agent.timeout == 60
        assert agent.retry_attempts == 5
    
    @patch('src.agents.cursor_agent.subprocess.run')
    def test_translate_success(self, mock_run):
        """Test successful translation."""
        mock_run.return_value = Mock(
            stdout="Bonjour le monde",
            stderr="",
            returncode=0
        )
        
        agent = CursorAgent({'retry_attempts': 1})
        result = agent.translate("Hello world", "en", "fr")
        
        assert isinstance(result, TranslationResult)
        assert result.translated_text == "Bonjour le monde"
        assert result.source_language == "en"
        assert result.target_language == "fr"
        assert result.agent_type == "cursor"
    
    @patch('src.agents.cursor_agent.subprocess.run')
    def test_translate_timeout(self, mock_run):
        """Test translation with timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired('cmd', 30)
        
        agent = CursorAgent({'retry_attempts': 1, 'retry_delay': 0})
        
        with pytest.raises(RuntimeError, match="Translation timeout"):
            agent.translate("Hello world", "en", "fr")
    
    @patch('src.agents.cursor_agent.subprocess.run')
    def test_translate_command_not_found(self, mock_run):
        """Test translation when command not found."""
        mock_run.side_effect = FileNotFoundError()
        
        agent = CursorAgent()
        
        with pytest.raises(RuntimeError, match="cursor-agent not found"):
            agent.translate("Hello world", "en", "fr")
    
    @patch('src.agents.cursor_agent.subprocess.run')
    def test_translate_empty_output(self, mock_run):
        """Test translation with empty output."""
        mock_run.return_value = Mock(stdout="", stderr="", returncode=0)
        
        agent = CursorAgent({'retry_attempts': 1})
        
        with pytest.raises(RuntimeError, match="Empty translation received"):
            agent.translate("Hello world", "en", "fr")


class TestAgentFactory:
    """Tests for AgentFactory."""
    
    def test_create_cursor_agent(self):
        """Test creating cursor agent."""
        agent = AgentFactory.create('cursor')
        assert isinstance(agent, CursorAgent)
        assert agent.get_agent_type() == 'cursor'
    
    def test_create_gemini_agent(self):
        """Test creating gemini agent."""
        agent = AgentFactory.create('gemini')
        assert isinstance(agent, GeminiAgent)
    
    def test_create_claude_agent(self):
        """Test creating claude agent."""
        agent = AgentFactory.create('claude')
        assert isinstance(agent, ClaudeAgent)
    
    def test_create_ollama_agent(self):
        """Test creating ollama agent."""
        agent = AgentFactory.create('ollama')
        assert isinstance(agent, OllamaAgent)
    
    def test_create_with_config(self):
        """Test creating agent with config."""
        config = {'timeout': 60}
        agent = AgentFactory.create('cursor', config)
        assert agent.timeout == 60
    
    def test_create_invalid_type(self):
        """Test creating agent with invalid type."""
        with pytest.raises(ValueError, match="Unsupported agent type"):
            AgentFactory.create('invalid')
    
    def test_get_supported_agents(self):
        """Test getting supported agents list."""
        agents = AgentFactory.get_supported_agents()
        assert 'cursor' in agents
        assert 'gemini' in agents
        assert 'claude' in agents
        assert 'ollama' in agents
    
    def test_register_new_agent(self):
        """Test registering a new agent type."""
        class CustomAgent(BaseAgent):
            def _setup(self):
                pass
            def get_agent_type(self):
                return 'custom'
            def translate(self, text, source_lang, target_lang):
                pass
        
        AgentFactory.register_agent('custom', CustomAgent)
        assert 'custom' in AgentFactory.get_supported_agents()
        
        agent = AgentFactory.create('custom')
        assert isinstance(agent, CustomAgent)

