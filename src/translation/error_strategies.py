import random
import string
from typing import Dict


KEYBOARD_NEIGHBORS = {
    'a': 'qwsz', 'b': 'vghn', 'c': 'xdfv', 'd': 'sfcxe', 'e': 'wrds',
    'f': 'dgcrv', 'g': 'fhvbt', 'h': 'gjbny', 'i': 'uojk', 'j': 'hkinu',
    'k': 'jlmo', 'l': 'kop', 'm': 'njk', 'n': 'bhjm', 'o': 'ipkl',
    'p': 'ol', 'q': 'wa', 'r': 'etfd', 's': 'awedxz', 't': 'ryfg',
    'u': 'yihj', 'v': 'cfgb', 'w': 'qeas', 'x': 'zsdc', 'y': 'tugh',
    'z': 'asx'
}


def character_swap(word: str, rng: random.Random) -> str:
    """
    Swap two adjacent characters.
    
    Args:
        word: Input word
        rng: Random number generator
        
    Returns:
        Word with swapped characters
    """
    if len(word) < 2:
        return word
    
    pos = rng.randint(0, len(word) - 2)
    word_list = list(word)
    word_list[pos], word_list[pos + 1] = word_list[pos + 1], word_list[pos]
    
    return ''.join(word_list)


def character_deletion(word: str, rng: random.Random) -> str:
    """
    Delete a random character.
    
    Args:
        word: Input word
        rng: Random number generator
        
    Returns:
        Word with deleted character
    """
    if len(word) < 2:
        return word
    
    pos = rng.randint(0, len(word) - 1)
    return word[:pos] + word[pos + 1:]


def character_insertion(word: str, rng: random.Random) -> str:
    """
    Insert a random character.
    
    Args:
        word: Input word
        rng: Random number generator
        
    Returns:
        Word with inserted character
    """
    pos = rng.randint(0, len(word))
    
    char_at_pos = word[pos - 1].lower() if pos > 0 else word[pos].lower() if pos < len(word) else 'e'
    
    if char_at_pos in KEYBOARD_NEIGHBORS:
        char = rng.choice(KEYBOARD_NEIGHBORS[char_at_pos])
    else:
        char = rng.choice(string.ascii_lowercase)
    
    return word[:pos] + char + word[pos:]


def character_substitution(word: str, rng: random.Random) -> str:
    """
    Substitute a character with keyboard neighbor.
    
    Args:
        word: Input word
        rng: Random number generator
        
    Returns:
        Word with substituted character
    """
    if len(word) < 1:
        return word
    
    pos = rng.randint(0, len(word) - 1)
    original_char = word[pos].lower()
    
    if original_char in KEYBOARD_NEIGHBORS:
        new_char = rng.choice(KEYBOARD_NEIGHBORS[original_char])
    else:
        new_char = rng.choice(string.ascii_lowercase)
    
    return word[:pos] + new_char + word[pos + 1:]


def get_error_types(rng: random.Random) -> list:
    """
    Get list of all error type functions.
    
    Args:
        rng: Random number generator
        
    Returns:
        List of error functions configured with rng
    """
    return [
        lambda word: character_swap(word, rng),
        lambda word: character_deletion(word, rng),
        lambda word: character_insertion(word, rng),
        lambda word: character_substitution(word, rng)
    ]

