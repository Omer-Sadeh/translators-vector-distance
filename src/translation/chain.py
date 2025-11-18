from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime

from src.agents.base import BaseAgent, TranslationResult
from src.translation.error_injector import ErrorInjector


@dataclass
class ChainResult:
    """Result of complete translation chain execution."""
    original_text: str
    corrupted_text: str
    error_rate_target: float
    error_rate_actual: float
    translation_fr: str
    translation_he: str
    translation_en: str
    agent_type: str
    total_duration_seconds: float
    individual_durations: Dict[str, float]
    success: bool
    error_message: Optional[str]
    timestamp: datetime
    metadata: Dict[str, Any]


class TranslationChain:
    """
    Orchestrates translation chain: EN → FR → HE → EN.
    
    Manages the complete flow of text through three translation stages,
    with optional error injection at the beginning.
    """
    
    def __init__(
        self,
        agent: BaseAgent,
        error_injector: Optional[ErrorInjector] = None
    ):
        """
        Initialize translation chain.
        
        Args:
            agent: Translation agent to use for all steps
            error_injector: Optional error injector (creates default if None)
        """
        self.agent = agent
        self.error_injector = error_injector or ErrorInjector()
        self._intermediate_translations: List[TranslationResult] = []
    
    def execute_chain(
        self,
        text: str,
        error_rate: float = 0.0
    ) -> ChainResult:
        """
        Execute complete translation chain with optional error injection.
        
        Args:
            text: Original English text
            error_rate: Error rate to inject (0.0 to 1.0)
            
        Returns:
            ChainResult containing all translations and metadata
            
        Raises:
            ValueError: If text is empty or error_rate is invalid
            RuntimeError: If any translation step fails
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        if not 0.0 <= error_rate <= 1.0:
            raise ValueError(f"Error rate must be between 0 and 1, got {error_rate}")
        
        start_time = datetime.now()
        self._intermediate_translations = []
        
        corrupted_text = self.error_injector.inject_errors(text, error_rate)
        actual_error_rate = self.error_injector.calculate_actual_error_rate(
            text, corrupted_text
        )
        
        try:
            result_fr = self._translate_step(corrupted_text, 'en', 'fr', 'step1_en_to_fr')
            result_he = self._translate_step(result_fr.translated_text, 'fr', 'he', 'step2_fr_to_he')
            result_en = self._translate_step(result_he.translated_text, 'he', 'en', 'step3_he_to_en')
            
            total_duration = (datetime.now() - start_time).total_seconds()
            
            return ChainResult(
                original_text=text,
                corrupted_text=corrupted_text,
                error_rate_target=error_rate,
                error_rate_actual=actual_error_rate,
                translation_fr=result_fr.translated_text,
                translation_he=result_he.translated_text,
                translation_en=result_en.translated_text,
                agent_type=self.agent.get_agent_type(),
                total_duration_seconds=total_duration,
                individual_durations={
                    'en_to_fr': result_fr.duration_seconds,
                    'fr_to_he': result_he.duration_seconds,
                    'he_to_en': result_en.duration_seconds
                },
                success=True,
                error_message=None,
                timestamp=start_time,
                metadata={
                    'word_count_original': len(text.split()),
                    'word_count_corrupted': len(corrupted_text.split()),
                    'agent_metadata': {
                        'en_to_fr': result_fr.metadata,
                        'fr_to_he': result_he.metadata,
                        'he_to_en': result_en.metadata
                    }
                }
            )
            
        except Exception as e:
            total_duration = (datetime.now() - start_time).total_seconds()
            
            return ChainResult(
                original_text=text,
                corrupted_text=corrupted_text,
                error_rate_target=error_rate,
                error_rate_actual=actual_error_rate,
                translation_fr=self._get_translation_or_empty(0),
                translation_he=self._get_translation_or_empty(1),
                translation_en=self._get_translation_or_empty(2),
                agent_type=self.agent.get_agent_type(),
                total_duration_seconds=total_duration,
                individual_durations=self._get_partial_durations(),
                success=False,
                error_message=str(e),
                timestamp=start_time,
                metadata={
                    'word_count_original': len(text.split()),
                    'word_count_corrupted': len(corrupted_text.split()),
                    'failed_at_step': len(self._intermediate_translations)
                }
            )
    
    def _translate_step(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        step_name: str
    ) -> TranslationResult:
        """
        Execute a single translation step.
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            step_name: Name of this step for logging
            
        Returns:
            TranslationResult from agent
            
        Raises:
            RuntimeError: If translation fails
        """
        try:
            result = self.agent.translate(text, source_lang, target_lang)
            self._intermediate_translations.append(result)
            return result
        except Exception as e:
            raise RuntimeError(f"Translation failed at {step_name}: {str(e)}") from e
    
    def _get_translation_or_empty(self, index: int) -> str:
        """
        Get intermediate translation by index or empty string.
        
        Args:
            index: Index in intermediate translations list
            
        Returns:
            Translation text or empty string
        """
        if 0 <= index < len(self._intermediate_translations):
            return self._intermediate_translations[index].translated_text
        return ""
    
    def _get_partial_durations(self) -> Dict[str, float]:
        """
        Get durations for completed steps.
        
        Returns:
            Dictionary of step durations
        """
        durations = {}
        steps = ['en_to_fr', 'fr_to_he', 'he_to_en']
        
        for i, step in enumerate(steps):
            if i < len(self._intermediate_translations):
                durations[step] = self._intermediate_translations[i].duration_seconds
            else:
                durations[step] = 0.0
        
        return durations
    
    def get_intermediate_translations(self) -> List[TranslationResult]:
        """
        Get list of intermediate translation results.
        
        Returns:
            List of TranslationResult objects from last chain execution
        """
        return self._intermediate_translations.copy()

