import subprocess
import time
from typing import Dict, Any
from datetime import datetime

from src.agents.base import BaseAgent, TranslationResult


class CursorAgent(BaseAgent):
    """Translation agent using cursor-agent CLI."""
    
    def _setup(self) -> None:
        """Setup cursor-agent configuration."""
        self.command = self.config.get('command', 'cursor-agent')
        self.args = self.config.get('args', ['-p'])
        self.timeout = self.config.get('timeout', 30)
        self.retry_attempts = self.config.get('retry_attempts', 3)
        self.retry_delay = self.config.get('retry_delay', 2)
    
    def get_agent_type(self) -> str:
        """Get agent type identifier."""
        return 'cursor'
    
    def _build_translation_prompt(
        self, 
        text: str, 
        source_lang: str, 
        target_lang: str
    ) -> str:
        """
        Build translation prompt for cursor-agent.
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Formatted prompt string
        """
        lang_names = {
            'en': 'English',
            'fr': 'French',
            'he': 'Hebrew'
        }
        
        source = lang_names.get(source_lang, source_lang)
        target = lang_names.get(target_lang, target_lang)
        
        prompt = (
            f"Translate the following text from {source} to {target}. "
            f"Provide ONLY the translation, no explanations or commentary.\n\n"
            f"Text: {text}\n\n"
            f"Translation:"
        )
        
        return prompt
    
    def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> TranslationResult:
        """
        Translate text using cursor-agent CLI.
        
        Args:
            text: Text to translate
            source_lang: Source language code (e.g., 'en', 'fr', 'he')
            target_lang: Target language code
            
        Returns:
            TranslationResult containing translated text and metadata
            
        Raises:
            ValueError: If input validation fails
            RuntimeError: If translation fails after retries
        """
        self.validate_input(text, source_lang, target_lang)
        self.before_translate(text, source_lang, target_lang)
        
        start_time = time.time()
        prompt = self._build_translation_prompt(text, source_lang, target_lang)
        
        last_error = None
        for attempt in range(self.retry_attempts):
            try:
                result = subprocess.run(
                    [self.command] + self.args + [prompt],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    check=True
                )
                
                translated_text = result.stdout.strip()
                
                if not translated_text:
                    raise RuntimeError("Empty translation received")
                
                duration = time.time() - start_time
                
                translation_result = TranslationResult(
                    translated_text=translated_text,
                    source_language=source_lang,
                    target_language=target_lang,
                    agent_type=self.get_agent_type(),
                    duration_seconds=duration,
                    metadata={
                        'attempt': attempt + 1,
                        'command': self.command,
                        'prompt_length': len(prompt)
                    },
                    timestamp=datetime.now()
                )
                
                self.after_translate(translation_result)
                return translation_result
                
            except subprocess.TimeoutExpired as e:
                last_error = RuntimeError(f"Translation timeout after {self.timeout}s")
            except subprocess.CalledProcessError as e:
                last_error = RuntimeError(f"cursor-agent failed: {e.stderr}")
            except FileNotFoundError:
                last_error = RuntimeError(
                    "cursor-agent not found. Please ensure it's installed and in PATH."
                )
                break
            except Exception as e:
                last_error = RuntimeError(f"Unexpected error: {str(e)}")
            
            if attempt < self.retry_attempts - 1:
                time.sleep(self.retry_delay * (attempt + 1))
        
        self.on_error(last_error)
        raise last_error

