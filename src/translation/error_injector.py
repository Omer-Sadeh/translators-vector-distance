import random
import string
from typing import Tuple

from src.translation.error_strategies import (
    get_error_types,
    KEYBOARD_NEIGHBORS
)


class ErrorInjector:
    """
    Introduces controlled spelling errors into text.
    
    Supports four types of errors: character swap, deletion, insertion,
    and substitution. Maintains word boundaries and punctuation.
    """
    
    def __init__(self, seed: int = None):
        """
        Initialize error injector.
        
        Args:
            seed: Random seed for reproducibility (optional)
        """
        self.random = random.Random(seed)
        self.keyboard_neighbors = KEYBOARD_NEIGHBORS
    
    def inject_errors(
        self,
        text: str,
        error_rate: float,
        maintain_punctuation: bool = True,
        maintain_capitalization: bool = True
    ) -> str:
        """
        Inject spelling errors into text at specified rate.
        
        Args:
            text: Input text
            error_rate: Target error rate (0.0 to 1.0)
            maintain_punctuation: Keep punctuation unchanged
            maintain_capitalization: Preserve capitalization patterns
            
        Returns:
            Text with injected errors
            
        Raises:
            ValueError: If error_rate is out of valid range
        """
        if not 0.0 <= error_rate <= 1.0:
            raise ValueError(f"Error rate must be between 0 and 1, got {error_rate}")
        
        if error_rate == 0.0:
            return text
        
        words = text.split()
        num_words_to_corrupt = max(1, int(len(words) * error_rate))
        
        indices_to_corrupt = self.random.sample(
            range(len(words)),
            min(num_words_to_corrupt, len(words))
        )
        
        corrupted_words = []
        for i, word in enumerate(words):
            if i in indices_to_corrupt:
                corrupted_word = self._corrupt_word(
                    word,
                    maintain_punctuation,
                    maintain_capitalization
                )
                corrupted_words.append(corrupted_word)
            else:
                corrupted_words.append(word)
        
        return ' '.join(corrupted_words)
    
    def _corrupt_word(
        self,
        word: str,
        maintain_punctuation: bool,
        maintain_capitalization: bool
    ) -> str:
        """
        Corrupt a single word with random error.
        
        Args:
            word: Word to corrupt
            maintain_punctuation: Keep punctuation unchanged
            maintain_capitalization: Preserve capitalization patterns
            
        Returns:
            Corrupted word
        """
        if len(word) < 2:
            return word
        
        leading_punct, core_word, trailing_punct = self._split_punctuation(word)
        
        if len(core_word) < 2:
            return word
        
        was_capitalized = core_word[0].isupper() if maintain_capitalization else False
        
        error_types = get_error_types(self.random)
        error_func = self.random.choice(error_types)
        corrupted = error_func(core_word.lower())
        
        if was_capitalized and len(corrupted) > 0:
            corrupted = corrupted[0].upper() + corrupted[1:]
        
        return leading_punct + corrupted + trailing_punct
    
    def _split_punctuation(self, word: str) -> Tuple[str, str, str]:
        """
        Split word into leading punctuation, core, trailing punctuation.
        
        Args:
            word: Input word
            
        Returns:
            Tuple of (leading_punct, core_word, trailing_punct)
        """
        leading = ''
        trailing = ''
        
        start = 0
        while start < len(word) and word[start] in string.punctuation:
            leading += word[start]
            start += 1
        
        end = len(word)
        while end > start and word[end - 1] in string.punctuation:
            trailing = word[end - 1] + trailing
            end -= 1
        
        core = word[start:end]
        
        return leading, core, trailing
    
    def calculate_actual_error_rate(self, original: str, corrupted: str) -> float:
        """
        Calculate actual error rate between two texts.
        
        Compares word-by-word and returns percentage of differing words.
        
        Args:
            original: Original text
            corrupted: Corrupted text
            
        Returns:
            Error rate (0.0 to 1.0)
        """
        original_words = original.split()
        corrupted_words = corrupted.split()
        
        if len(original_words) == 0:
            return 0.0
        
        if len(original_words) != len(corrupted_words):
            return min(len(original_words), len(corrupted_words)) / len(original_words)
        
        differences = sum(
            1 for o, c in zip(original_words, corrupted_words) if o != c
        )
        
        return differences / len(original_words)
    
    _character_swap = lambda self, word: get_error_types(self.random)[0](word)
    _character_deletion = lambda self, word: get_error_types(self.random)[1](word)
    _character_insertion = lambda self, word: get_error_types(self.random)[2](word)
    _character_substitution = lambda self, word: get_error_types(self.random)[3](word)
