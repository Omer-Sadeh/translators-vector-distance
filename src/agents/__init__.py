"""Agent implementations for translation."""

from src.agents.base import BaseAgent, TranslationResult
from src.agents.cursor_agent import CursorAgent
from src.agents.gemini_agent import GeminiAgent
from src.agents.claude_agent import ClaudeAgent
from src.agents.ollama_agent import OllamaAgent
from src.agents.factory import AgentFactory

__all__ = [
    'BaseAgent',
    'TranslationResult',
    'CursorAgent',
    'GeminiAgent',
    'ClaudeAgent',
    'OllamaAgent',
    'AgentFactory'
]

