import subprocess
import time
from typing import Dict, Any
from datetime import datetime

from src.agents.base import BaseAgent, TranslationResult


class OllamaAgent(BaseAgent):
    """Translation agent using Ollama for local LLM."""
    
    def _setup(self) -> None:
        """Setup Ollama configuration."""
        self.command = self.config.get('command', 'ollama')
        self.model = self.config.get('model', 'llama3.2')
        self.args = self.config.get('args', ['run', self.model])
        self.timeout = self.config.get('timeout', 30)
        self.retry_attempts = self.config.get('retry_attempts', 3)
        self.retry_delay = self.config.get('retry_delay', 2)
        self.auto_start = self.config.get('auto_start', True)
        self.startup_wait = self.config.get('startup_wait', 5)
        
        if not self._check_ollama_running():
            if self.auto_start:
                self._start_ollama()
            else:
                raise RuntimeError(
                    "Ollama is not running. Please start it with 'ollama serve' "
                    "or enable auto_start in config."
                )
    
    def _check_ollama_running(self) -> bool:
        """
        Check if Ollama service is running.
        
        Returns:
            True if Ollama is responding, False otherwise
        """
        try:
            result = subprocess.run(
                [self.command, 'list'],
                capture_output=True,
                text=True,
                timeout=5,
                check=False
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _start_ollama(self) -> None:
        """
        Start Ollama service in the background.
        
        Raises:
            RuntimeError: If service fails to start
        """
        try:
            subprocess.Popen(
                [self.command, 'serve'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            
            time.sleep(self.startup_wait)
            
            max_retries = 3
            for attempt in range(max_retries):
                if self._check_ollama_running():
                    return
                time.sleep(2)
            
            raise RuntimeError(
                f"Failed to start Ollama after {self.startup_wait + max_retries * 2}s"
            )
            
        except FileNotFoundError:
            raise RuntimeError(
                "Ollama not found. Please ensure it's installed and in PATH."
            )
        except Exception as e:
            raise RuntimeError(f"Failed to start Ollama: {str(e)}")
    
    def get_agent_type(self) -> str:
        """Get agent type identifier."""
        return 'ollama'
    
    def _build_translation_prompt(
        self, 
        text: str, 
        source_lang: str, 
        target_lang: str
    ) -> str:
        """
        Build translation prompt for Ollama.
        
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
            f"Translate the following {source} text to {target}. "
            f"Return ONLY the translated text without any explanations.\n\n"
            f"Text to translate:\n{text}\n\n"
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
        Translate text using Ollama.
        
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
                        'model': self.model,
                        'prompt_length': len(prompt)
                    },
                    timestamp=datetime.now()
                )
                
                self.after_translate(translation_result)
                return translation_result
                
            except subprocess.TimeoutExpired as e:
                last_error = RuntimeError(f"Translation timeout after {self.timeout}s")
            except subprocess.CalledProcessError as e:
                last_error = RuntimeError(f"Ollama failed: {e.stderr}")
            except FileNotFoundError:
                last_error = RuntimeError(
                    "Ollama not found. Please ensure it's installed and in PATH."
                )
                break
            except Exception as e:
                last_error = RuntimeError(f"Unexpected error: {str(e)}")
            
            if attempt < self.retry_attempts - 1:
                time.sleep(self.retry_delay * (attempt + 1))
        
        self.on_error(last_error)
        raise last_error

