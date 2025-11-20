# Plugin Architecture Diagram

## Agent Plugin System

```mermaid
classDiagram
    class BaseAgent {
        <<abstract>>
        +command: str
        +timeout: int
        +translate(text, source, target) TranslationResult
        +validate_input(text, source, target) void
        +get_agent_type() str
        #before_translate(text, source, target) void
        #after_translate(result) void
        #on_error(error) void
        -_execute_command(text, source, target) str
        -_parse_output(output) str
    }
    
    class CursorAgent {
        +command = "cursor-agent"
        +get_agent_type() "cursor"
    }
    
    class GeminiAgent {
        +command = "gemini"
        +get_agent_type() "gemini"
    }
    
    class ClaudeAgent {
        +command = "claude"
        +get_agent_type() "claude"
    }
    
    class OllamaAgent {
        +command = "ollama"
        +model: str
        +get_agent_type() "ollama"
    }
    
    class AgentFactory {
        <<factory>>
        +create_agent(agent_type, config) BaseAgent
        +get_available_agents() List~str~
    }
    
    class TranslationResult {
        +translated_text: str
        +source_language: str
        +target_language: str
        +agent_type: str
        +duration_seconds: float
        +metadata: dict
        +timestamp: datetime
    }
    
    BaseAgent <|-- CursorAgent
    BaseAgent <|-- GeminiAgent
    BaseAgent <|-- ClaudeAgent
    BaseAgent <|-- OllamaAgent
    AgentFactory ..> BaseAgent : creates
    BaseAgent ..> TranslationResult : returns
```

## Plugin Architecture Benefits

1. **Extensibility**: New agents added by subclassing `BaseAgent`
2. **Consistency**: Common interface ensures uniform behavior
3. **Lifecycle Hooks**: `before_translate`, `after_translate`, `on_error`
4. **Factory Pattern**: Centralized agent instantiation
5. **Configuration**: Agent-specific settings via config

## Adding a New Agent

```python
from src.agents.base import BaseAgent, TranslationResult

class MyCustomAgent(BaseAgent):
    def __init__(self, command="my-agent", **kwargs):
        super().__init__(command, **kwargs)
    
    def get_agent_type(self) -> str:
        return "custom"
    
    # Optional: Override hooks
    def before_translate(self, text, source, target):
        print(f"Translating {source} → {target}")
```

Register in `AgentFactory`:

```python
# src/agents/factory.py
AGENT_CLASSES = {
    'cursor': CursorAgent,
    'gemini': GeminiAgent,
    'claude': ClaudeAgent,
    'ollama': OllamaAgent,
    'custom': MyCustomAgent  # Add here
}
```

