"""
Example Custom Translation Agent

This file demonstrates how to create a fully-featured custom translation agent
with all best practices: error handling, logging, hooks, caching, and rate limiting.
"""

from src.agents.base import BaseAgent, TranslationResult
from datetime import datetime
from typing import Optional, Dict
import logging
import hashlib
from time import time, sleep


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExampleCustomAgent(BaseAgent):
    """
    Example custom translation agent with full features.
    
    Demonstrates:
    - Configuration handling
    - Lifecycle hooks
    - Caching
    - Rate limiting
    - Error handling
    - Logging
    - Metadata tracking
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize example custom agent.
        
        Args:
            config: Configuration dictionary with keys:
                - api_key: API key for translation service
                - model: Model name to use
                - temperature: Temperature parameter (0.0-1.0)
                - rate_limit: Max requests per minute
                - timeout: Timeout in seconds
                - enable_cache: Whether to enable caching
        """
        super().__init__(config)
        
        # Extract configuration with defaults
        self.api_key = self.config.get('api_key', 'demo-key')
        self.model_name = self.config.get('model', 'translation-model-v1')
        self.temperature = self.config.get('temperature', 0.7)
        self.rate_limit = self.config.get('rate_limit', 60)
        self.timeout = self.config.get('timeout', 30)
        self.enable_cache = self.config.get('enable_cache', True)
        
        # Initialize cache
        self.cache = {} if self.enable_cache else None
        
        # Initialize rate limiting
        self.request_times = []
        
        logger.info(
            f"Initialized ExampleCustomAgent",
            extra={
                'model': self.model_name,
                'rate_limit': self.rate_limit,
                'cache_enabled': self.enable_cache
            }
        )
    
    def get_agent_type(self) -> str:
        """Return unique identifier for this agent."""
        return "example_custom"
    
    def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> TranslationResult:
        """
        Perform translation using custom service.
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            TranslationResult with translation and metadata
            
        Raises:
            ValueError: If input validation fails
            RuntimeError: If translation fails
        """
        # Validate input
        self.validate_input(text, source_lang, target_lang)
        
        # Check cache first
        if self.enable_cache:
            cache_key = self._get_cache_key(text, source_lang, target_lang)
            if cache_key in self.cache:
                logger.info("Cache hit for translation")
                return self.cache[cache_key]
        
        # Apply rate limiting
        self._enforce_rate_limit()
        
        # Call before_translate hook
        self.before_translate(text, source_lang, target_lang)
        
        start_time = datetime.now()
        
        try:
            # Simulate translation (in real implementation, call actual API)
            translated_text = self._call_translation_api(
                text, source_lang, target_lang
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            # Build result
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
                    'cached': False,
                    'api_version': '2.0',
                    'confidence_score': 0.95,
                    'word_count': len(text.split()),
                }
            )
            
            # Store in cache
            if self.enable_cache:
                self.cache[cache_key] = result
                logger.debug(f"Stored result in cache (key: {cache_key[:8]}...)")
            
            # Call after_translate hook
            self.after_translate(result)
            
            return result
            
        except Exception as e:
            # Call error hook
            self.on_error(e, text, source_lang, target_lang)
            
            # Re-raise with context
            raise RuntimeError(
                f"Translation failed: {type(e).__name__}: {str(e)}"
            ) from e
    
    def _call_translation_api(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> str:
        """
        Call translation API (simulated).
        
        In a real implementation, this would make an HTTP request
        to your translation service.
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Translated text
            
        Raises:
            RuntimeError: If API call fails
        """
        # Simulate API call delay
        sleep(0.1)
        
        # Simulate translation by prefixing with target language
        # In real implementation:
        # response = requests.post(
        #     f"https://api.example.com/v2/translate",
        #     headers={"Authorization": f"Bearer {self.api_key}"},
        #     json={
        #         "text": text,
        #         "source": source_lang,
        #         "target": target_lang,
        #         "model": self.model_name,
        #         "temperature": self.temperature
        #     },
        #     timeout=self.timeout
        # )
        # 
        # if response.status_code != 200:
        #     raise RuntimeError(f"API error: {response.status_code}")
        # 
        # return response.json()["translation"]
        
        return f"[{target_lang.upper()}] {text}"
    
    def _get_cache_key(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> str:
        """
        Generate cache key for translation request.
        
        Args:
            text: Text to translate
            source_lang: Source language
            target_lang: Target language
            
        Returns:
            MD5 hash as cache key
        """
        content = f"{text}|{source_lang}|{target_lang}|{self.model_name}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _enforce_rate_limit(self) -> None:
        """
        Enforce rate limiting based on configuration.
        
        Blocks execution if rate limit would be exceeded.
        """
        now = time()
        
        # Remove timestamps older than 1 minute
        self.request_times = [
            t for t in self.request_times 
            if now - t < 60
        ]
        
        # Check if we've hit the rate limit
        if len(self.request_times) >= self.rate_limit:
            oldest = self.request_times[0]
            wait_time = 60 - (now - oldest)
            
            if wait_time > 0:
                logger.warning(
                    f"Rate limit reached ({self.rate_limit}/min), "
                    f"waiting {wait_time:.1f}s"
                )
                sleep(wait_time)
                # Refresh timestamp list after waiting
                self.request_times = []
        
        # Record this request
        self.request_times.append(time())
    
    def before_translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> None:
        """
        Hook called before translation.
        
        Use for logging, preprocessing, validation, etc.
        """
        super().before_translate(text, source_lang, target_lang)
        
        logger.info(
            f"Starting translation",
            extra={
                'agent': self.get_agent_type(),
                'direction': f"{source_lang} → {target_lang}",
                'text_length': len(text),
                'word_count': len(text.split()),
                'model': self.model_name
            }
        )
    
    def after_translate(self, result: TranslationResult) -> None:
        """
        Hook called after successful translation.
        
        Use for logging, postprocessing, metrics, etc.
        """
        super().after_translate(result)
        
        logger.info(
            f"Translation completed",
            extra={
                'agent': result.agent_type,
                'duration': f"{result.duration_seconds:.2f}s",
                'success': result.success,
                'output_length': len(result.translated_text)
            }
        )
    
    def on_error(
        self,
        error: Exception,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> None:
        """
        Hook called when translation fails.
        
        Use for error logging, recovery, alerting, etc.
        """
        super().on_error(error, text, source_lang, target_lang)
        
        logger.error(
            f"Translation failed",
            extra={
                'agent': self.get_agent_type(),
                'error_type': type(error).__name__,
                'error_message': str(error),
                'direction': f"{source_lang} → {target_lang}",
                'text_length': len(text)
            },
            exc_info=True
        )
    
    def clear_cache(self) -> int:
        """
        Clear translation cache.
        
        Returns:
            Number of entries cleared
        """
        if self.cache is None:
            return 0
        
        count = len(self.cache)
        self.cache.clear()
        logger.info(f"Cleared {count} cache entries")
        return count
    
    def get_cache_stats(self) -> Dict:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        if self.cache is None:
            return {'enabled': False, 'size': 0}
        
        return {
            'enabled': True,
            'size': len(self.cache),
            'entries': list(self.cache.keys())
        }


# Example usage
if __name__ == "__main__":
    # Configure agent
    config = {
        'api_key': 'demo-api-key',
        'model': 'advanced-translator-v2',
        'temperature': 0.8,
        'rate_limit': 10,  # 10 requests per minute
        'timeout': 30,
        'enable_cache': True
    }
    
    # Create agent
    agent = ExampleCustomAgent(config)
    
    # Test translation
    print("\n=== Example Translation ===")
    result = agent.translate("Hello, world!", "en", "fr")
    print(f"Original: {result.original_text}")
    print(f"Translated: {result.translated_text}")
    print(f"Duration: {result.duration_seconds:.2f}s")
    print(f"Metadata: {result.metadata}")
    
    # Test caching (should be instant)
    print("\n=== Cached Translation ===")
    result2 = agent.translate("Hello, world!", "en", "fr")
    print(f"Duration: {result2.duration_seconds:.4f}s (cached)")
    
    # Check cache stats
    print("\n=== Cache Statistics ===")
    stats = agent.get_cache_stats()
    print(f"Cache enabled: {stats['enabled']}")
    print(f"Cache size: {stats['size']}")
    
    # Test different translation
    print("\n=== Different Translation ===")
    result3 = agent.translate("Goodbye", "en", "es")
    print(f"Translated: {result3.translated_text}")
    
    # Register with factory for use in experiments
    from src.agents.factory import AgentFactory
    AgentFactory.register_agent('example_custom', ExampleCustomAgent)
    print("\n✓ Agent registered as 'example_custom'")
    print("  Add to config/experiment_config.yaml under 'agents' section")
    print("  Then use: ExperimentRunner('example_custom')")
