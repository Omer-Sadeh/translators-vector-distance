from typing import Dict, Any, Optional

from src.agents.base import BaseAgent
from src.agents.cursor_agent import CursorAgent
from src.agents.gemini_agent import GeminiAgent
from src.agents.claude_agent import ClaudeAgent
from src.agents.ollama_agent import OllamaAgent


class AgentFactory:
    """
    Factory for creating translation agent instances.
    
    Implements factory pattern for agent instantiation with
    configuration management.
    """
    
    _agent_classes = {
        'cursor': CursorAgent,
        'gemini': GeminiAgent,
        'claude': ClaudeAgent,
        'ollama': OllamaAgent
    }
    
    @classmethod
    def create(
        cls,
        agent_type: str,
        config: Optional[Dict[str, Any]] = None
    ) -> BaseAgent:
        """
        Create an agent instance of specified type.
        
        Args:
            agent_type: Type of agent to create ('cursor', 'gemini', 'claude', 'ollama')
            config: Optional configuration dictionary
            
        Returns:
            BaseAgent instance
            
        Raises:
            ValueError: If agent_type is not supported
        """
        agent_type = agent_type.lower()
        
        if agent_type not in cls._agent_classes:
            supported = ', '.join(cls._agent_classes.keys())
            raise ValueError(
                f"Unsupported agent type: {agent_type}. "
                f"Supported types: {supported}"
            )
        
        agent_class = cls._agent_classes[agent_type]
        return agent_class(config=config)
    
    @classmethod
    def get_supported_agents(cls) -> list:
        """
        Get list of supported agent types.
        
        Returns:
            List of agent type strings
        """
        return list(cls._agent_classes.keys())
    
    @classmethod
    def register_agent(cls, agent_type: str, agent_class: type) -> None:
        """
        Register a new agent type.
        
        Allows for dynamic extension of supported agents.
        
        Args:
            agent_type: Unique identifier for the agent
            agent_class: Agent class (must inherit from BaseAgent)
            
        Raises:
            TypeError: If agent_class doesn't inherit from BaseAgent
        """
        if not issubclass(agent_class, BaseAgent):
            raise TypeError(
                f"Agent class must inherit from BaseAgent, got {agent_class}"
            )
        
        cls._agent_classes[agent_type.lower()] = agent_class

