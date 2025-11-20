# Plugin Development Guide

## Overview

The Translation Vector Distance Analysis system uses a plugin architecture that allows you to easily add custom translation agents. This guide walks you through creating your own translation agent plugin.

## Architecture

### Plugin System

The system uses an abstract base class (`BaseAgent`) that defines the interface all translation agents must implement. New agents are registered with the `AgentFactory`, which handles instantiation and configuration.

**Key Components:**
- `BaseAgent` - Abstract base class defining the agent interface
- `AgentFactory` - Factory for creating and registering agents  
- Lifecycle hooks - Methods for customizing behavior at different stages
- Configuration system - YAML-based configuration for agent parameters

### Lifecycle Hooks

Translation agents support three lifecycle hooks that allow you to customize behavior:

1. `before_translate(text, source_lang, target_lang)` - Called before translation
2. `after_translate(result)` - Called after successful translation
3. `on_error(error, text, source_lang, target_lang)` - Called when translation fails

## Creating a Custom Agent

### Step 1: Create Agent Class

Create a new file in `src/agents/` (e.g., `my_custom_agent.py`):

```python
from src.agents.base import BaseAgent, TranslationResult
from datetime import datetime
from typing import Optional


class MyCustomAgent(BaseAgent):
    """
    Custom translation agent implementation.
    
    This example shows how to integrate with any translation service.
    """
    
    def __init__(self, config: Optional[dict] = None):
        """
        Initialize your custom agent.
        
        Args:
            config: Configuration dictionary from YAML
        """
        super().__init__(config)
        
        # Extract configuration parameters
        self.api_key = config.get('api_key') if config else None
        self.model_name = config.get('model', 'default')
        self.temperature = config.get('temperature', 0.7)
        
        # Initialize your translation service
        # self.client = MyTranslationService(api_key=self.api_key)
    
    def get_agent_type(self) -> str:
        """Return unique identifier for this agent type."""
        return "my_custom"
    
    def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> TranslationResult:
        """
        Perform translation using your service.
        
        Args:
            text: Text to translate
            source_lang: Source language code (e.g., 'en', 'fr')
            target_lang: Target language code
            
        Returns:
            TranslationResult with translation and metadata
            
        Raises:
            ValueError: If validation fails
            RuntimeError: If translation fails
        """
        # Validate input using base class method
        self.validate_input(text, source_lang, target_lang)
        
        # Call before_translate hook
        self.before_translate(text, source_lang, target_lang)
        
        start_time = datetime.now()
        
        try:
            # YOUR TRANSLATION LOGIC HERE
            # Example using a hypothetical API:
            # translated_text = self.client.translate(
            #     text=text,
            #     source=source_lang,
            #     target=target_lang,
            #     model=self.model_name
            # )
            
            # For demonstration, we'll use a placeholder
            translated_text = f"[{target_lang.upper()}] {text}"
            
            duration = (datetime.now() - start_time).total_seconds()
            
            result = TranslationResult(
                original_text=text,
                translated_text=translated_text,
                source_lang=source_lang,
                target_lang=target_lang,
                agent_type=self.get_agent_type(),
                duration_seconds=duration,
                success=True,
                error_message=None,
                metadata={
                    'model': self.model_name,
                    'temperature': self.temperature,
                    # Add any service-specific metadata
                }
            )
            
            # Call after_translate hook
            self.after_translate(result)
            
            return result
            
        except Exception as e:
            # Call error hook
            self.on_error(e, text, source_lang, target_lang)
            
            # Re-raise or return error result
            raise RuntimeError(f"Translation failed: {str(e)}") from e
    
    def before_translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> None:
        """
        Hook called before translation.
        
        Use this for logging, preprocessing, rate limiting, etc.
        """
        super().before_translate(text, source_lang, target_lang)
        # Add custom preprocessing here
        print(f"[MyCustomAgent] Translating: {source_lang} → {target_lang}")
    
    def after_translate(self, result: TranslationResult) -> None:
        """
        Hook called after successful translation.
        
        Use this for logging, postprocessing, caching, etc.
        """
        super().after_translate(result)
        # Add custom postprocessing here
        print(f"[MyCustomAgent] Completed in {result.duration_seconds:.2f}s")
    
    def on_error(
        self,
        error: Exception,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> None:
        """
        Hook called when translation fails.
        
        Use this for error logging, recovery, alerting, etc.
        """
        super().on_error(error, text, source_lang, target_lang)
        # Add custom error handling here
        print(f"[MyCustomAgent] Error: {type(error).__name__}: {str(error)}")
```

### Step 2: Register Agent with Factory

In your agent file, add registration:

```python
# At the bottom of my_custom_agent.py
from src.agents.factory import AgentFactory

AgentFactory.register_agent('my_custom', MyCustomAgent)
```

Or register it in your application code:

```python
from src.agents.factory import AgentFactory
from src.agents.my_custom_agent import MyCustomAgent

AgentFactory.register_agent('my_custom', MyCustomAgent)
```

### Step 3: Add Configuration

Add agent configuration to `config/experiment_config.yaml`:

```yaml
agents:
  my_custom:
    api_key: "your-api-key-here"  # Or use environment variable
    model: "best-model-v2"
    temperature: 0.7
    timeout: 30
    retry_attempts: 3
    retry_delay: 2
```

### Step 4: Use Your Agent

```python
from src.agents.factory import AgentFactory
from src.config import get_settings

# Get configuration
settings = get_settings()
config = settings.get_agent_config('my_custom')

# Create agent instance
agent = AgentFactory.create('my_custom', config)

# Use agent for translation
result = agent.translate(
    text="Hello, world!",
    source_lang="en",
    target_lang="fr"
)

print(f"Translation: {result.translated_text}")
print(f"Duration: {result.duration_seconds:.2f}s")
```

## Advanced Topics

### Implementing Retry Logic

```python
from time import sleep

def translate(self, text, source_lang, target_lang):
    self.validate_input(text, source_lang, target_lang)
    
    max_retries = self.config.get('retry_attempts', 3)
    retry_delay = self.config.get('retry_delay', 2)
    
    for attempt in range(max_retries):
        try:
            return self._do_translate(text, source_lang, target_lang)
        except Exception as e:
            if attempt < max_retries - 1:
                sleep(retry_delay)
                continue
            else:
                raise RuntimeError(f"Failed after {max_retries} attempts") from e
```

### Handling Timeouts

```python
import subprocess
from subprocess import TimeoutExpired

def translate(self, text, source_lang, target_lang):
    timeout = self.config.get('timeout', 30)
    
    try:
        result = subprocess.run(
            ['my-translator', '--source', source_lang, '--target', target_lang],
            input=text,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Translation failed: {result.stderr}")
        
        return result.stdout.strip()
        
    except TimeoutExpired:
        raise RuntimeError(f"Translation timed out after {timeout}s")
```

### Adding Caching

```python
from functools import lru_cache
import hashlib

class CachedAgent(BaseAgent):
    def __init__(self, config=None):
        super().__init__(config)
        self.cache = {}
    
    def _cache_key(self, text, source_lang, target_lang):
        """Generate cache key for translation."""
        content = f"{text}|{source_lang}|{target_lang}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def translate(self, text, source_lang, target_lang):
        # Check cache
        cache_key = self._cache_key(text, source_lang, target_lang)
        if cache_key in self.cache:
            print("Cache hit!")
            return self.cache[cache_key]
        
        # Perform translation
        result = self._do_translate(text, source_lang, target_lang)
        
        # Store in cache
        self.cache[cache_key] = result
        return result
```

### Rate Limiting

```python
from time import time, sleep

class RateLimitedAgent(BaseAgent):
    def __init__(self, config=None):
        super().__init__(config)
        self.requests_per_minute = config.get('rate_limit', 60)
        self.request_times = []
    
    def _wait_for_rate_limit(self):
        """Enforce rate limiting."""
        now = time()
        
        # Remove timestamps older than 1 minute
        self.request_times = [t for t in self.request_times if now - t < 60]
        
        # Check if we've hit the limit
        if len(self.request_times) >= self.requests_per_minute:
            oldest = self.request_times[0]
            wait_time = 60 - (now - oldest)
            if wait_time > 0:
                print(f"Rate limit reached, waiting {wait_time:.1f}s...")
                sleep(wait_time)
        
        # Record this request
        self.request_times.append(time())
    
    def translate(self, text, source_lang, target_lang):
        self._wait_for_rate_limit()
        return super().translate(text, source_lang, target_lang)
```

## Testing Your Agent

Create tests in `tests/test_agents.py`:

```python
import pytest
from src.agents.my_custom_agent import MyCustomAgent


class TestMyCustomAgent:
    """Tests for MyCustomAgent."""
    
    def test_initialization(self):
        """Test agent initialization."""
        config = {'model': 'test-model', 'temperature': 0.5}
        agent = MyCustomAgent(config)
        assert agent.get_agent_type() == "my_custom"
        assert agent.model_name == 'test-model'
        assert agent.temperature == 0.5
    
    def test_translate_success(self):
        """Test successful translation."""
        agent = MyCustomAgent()
        result = agent.translate("Hello", "en", "fr")
        
        assert result.success is True
        assert result.translated_text is not None
        assert result.agent_type == "my_custom"
        assert result.duration_seconds > 0
    
    def test_translate_empty_text(self):
        """Test translation with empty text raises error."""
        agent = MyCustomAgent()
        with pytest.raises(ValueError, match="Text cannot be empty"):
            agent.translate("", "en", "fr")
    
    def test_translate_same_language(self):
        """Test translation with same source/target raises error."""
        agent = MyCustomAgent()
        with pytest.raises(ValueError, match="must be different"):
            agent.translate("Hello", "en", "en")
```

Run tests:

```bash
pytest tests/test_agents.py::TestMyCustomAgent -v
```

## Best Practices

### 1. Error Handling

Always validate inputs and provide clear error messages:

```python
if not api_key:
    raise ValueError("API key is required for MyCustomAgent")

if response.status_code != 200:
    raise RuntimeError(f"API error: {response.status_code} - {response.text}")
```

### 2. Logging

Use structured logging for debugging:

```python
import logging

logger = logging.getLogger(__name__)

def translate(self, text, source_lang, target_lang):
    logger.info(
        f"Starting translation",
        extra={
            'agent': self.get_agent_type(),
            'source_lang': source_lang,
            'target_lang': target_lang,
            'text_length': len(text)
        }
    )
```

### 3. Configuration

Use configuration for all tunable parameters:

```python
# Don't hardcode values
timeout = 30  # BAD

# Use configuration
timeout = self.config.get('timeout', 30)  # GOOD
```

### 4. Metadata

Include useful metadata in results:

```python
metadata={
    'model': self.model_name,
    'tokens_used': response.usage.total_tokens,
    'api_version': response.version,
    'confidence_score': response.confidence,
    'detected_language': response.detected_source_lang
}
```

### 5. Resource Cleanup

Clean up resources in hooks:

```python
def __del__(self):
    """Cleanup when agent is destroyed."""
    if hasattr(self, 'client'):
        self.client.close()
```

## Common Pitfalls

### 1. Not Calling Parent Hooks

Always call parent class hooks:

```python
def before_translate(self, text, source_lang, target_lang):
    super().before_translate(text, source_lang, target_lang)  # IMPORTANT
    # Your code here
```

### 2. Forgetting to Validate

Use the base class validation:

```python
def translate(self, text, source_lang, target_lang):
    self.validate_input(text, source_lang, target_lang)  # REQUIRED
    # Translation logic...
```

### 3. Not Handling Timeouts

Always set reasonable timeouts:

```python
# BAD - can hang forever
response = requests.post(url, data=payload)

# GOOD - fails after timeout
response = requests.post(url, data=payload, timeout=30)
```

### 4. Hardcoding Language Codes

Support flexible language code formats:

```python
def _normalize_lang_code(self, code):
    """Normalize language code to service format."""
    # Handle different formats: 'en', 'en-US', 'eng'
    return code.lower().split('-')[0][:2]
```

## Example: Real API Integration

See `examples/custom_agent_example.py` for a complete working example that demonstrates:
- API authentication
- Request/response handling
- Error recovery
- Comprehensive logging
- Metadata extraction
- All lifecycle hooks

## Support

For questions or issues:
1. Check `docs/API.md` for API reference
2. Review existing agent implementations in `src/agents/`
3. Look at test examples in `tests/test_agents.py`
4. Consult `docs/ARCHITECTURE.md` for system design

## Summary

Creating a custom agent involves:
1. **Subclass** `BaseAgent`
2. **Implement** `translate()` and `get_agent_type()`
3. **Register** with `AgentFactory`
4. **Configure** in YAML
5. **Test** thoroughly
6. **Document** configuration options

Happy plugin development!
