from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TranslationResult:
    """Result of a translation operation."""
    translated_text: str
    source_language: str
    target_language: str
    agent_type: str
    duration_seconds: float
    metadata: Dict[str, Any]
    timestamp: datetime
    error: Optional[str] = None


class BaseAgent(ABC):
    """
    Abstract base class for translation agents.
    
    Provides plugin architecture with lifecycle hooks for extensibility.
    Each agent implementation communicates with a specific LLM CLI tool.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the agent.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self._setup()
    
    @abstractmethod
    def _setup(self) -> None:
        """Setup hook called during initialization."""
        pass
    
    @abstractmethod
    def get_agent_type(self) -> str:
        """
        Get the type identifier for this agent.
        
        Returns:
            Agent type string (e.g., 'cursor', 'gemini', 'claude', 'ollama')
        """
        pass
    
    @abstractmethod
    def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> TranslationResult:
        """
        Translate text from source language to target language.
        
        Args:
            text: Text to translate
            source_lang: Source language code (e.g., 'en', 'fr', 'he')
            target_lang: Target language code
            
        Returns:
            TranslationResult containing translated text and metadata
            
        Raises:
            ValueError: If text is empty or languages are invalid
            RuntimeError: If translation fails
        """
        pass
    
    def validate_input(self, text: str, source_lang: str, target_lang: str) -> None:
        """
        Validate translation input parameters.
        
        Args:
            text: Text to validate
            source_lang: Source language code
            target_lang: Target language code
            
        Raises:
            ValueError: If any parameter is invalid
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        valid_languages = {'en', 'fr', 'he'}
        if source_lang not in valid_languages:
            raise ValueError(f"Invalid source language: {source_lang}")
        if target_lang not in valid_languages:
            raise ValueError(f"Invalid target language: {target_lang}")
        if source_lang == target_lang:
            raise ValueError("Source and target languages must be different")
    
    def before_translate(self, text: str, source_lang: str, target_lang: str) -> None:
        """Hook called before translation. Override for custom behavior."""
        pass
    
    def after_translate(self, result: TranslationResult) -> None:
        """Hook called after translation. Override for custom behavior."""
        pass
    
    def on_error(self, error: Exception) -> None:
        """Hook called when translation fails. Override for custom error handling."""
        pass

