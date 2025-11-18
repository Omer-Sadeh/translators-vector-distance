import json
from typing import List, Dict
from pathlib import Path


class SentenceGenerator:
    """
    Generator and manager for test sentences.
    
    Provides curated English sentences with minimum 15 words
    for translation experiments.
    """
    
    DEFAULT_SENTENCES = [
        "The quick brown fox jumps over the lazy dog while the sun shines brightly in the clear blue sky.",
        "Artificial intelligence and machine learning are revolutionizing the way we interact with technology in our daily lives.",
        "Climate change poses significant challenges to global ecosystems and requires immediate action from governments worldwide.",
        "The ancient library contained thousands of manuscripts that revealed fascinating insights into historical civilizations and cultures.",
        "Modern transportation systems including high-speed trains and electric vehicles are transforming urban mobility and reducing emissions.",
        "Scientific research continues to uncover remarkable discoveries about the universe and our place within it.",
        "Education systems around the world are adapting to incorporate digital technologies and online learning platforms effectively.",
        "Healthcare professionals work tirelessly to provide quality medical care and improve patient outcomes in challenging conditions.",
        "Cultural diversity enriches our communities and promotes understanding between people from different backgrounds and traditions.",
        "The development of renewable energy sources is essential for achieving sustainable economic growth and environmental protection.",
        "International cooperation and diplomacy play crucial roles in maintaining global peace and addressing transnational challenges.",
        "Archaeological excavations have revealed ancient settlements that provide valuable information about human civilization development and cultural evolution.",
        "The digital revolution has fundamentally transformed how we communicate, work, and access information in modern society.",
        "Biodiversity conservation efforts aim to protect endangered species and preserve natural habitats for future generations.",
        "Space exploration programs continue to expand our knowledge of distant planets and the mysteries of the cosmos."
    ]
    
    def __init__(self):
        """Initialize sentence generator."""
        self.sentences = self.DEFAULT_SENTENCES.copy()
    
    def get_sentences(self, count: int = None) -> List[str]:
        """
        Get test sentences.
        
        Args:
            count: Number of sentences to return (None for all)
            
        Returns:
            List of sentences
        """
        if count is None:
            return self.sentences.copy()
        return self.sentences[:min(count, len(self.sentences))]
    
    def add_sentence(self, sentence: str) -> None:
        """
        Add a custom sentence.
        
        Args:
            sentence: Sentence to add
            
        Raises:
            ValueError: If sentence is too short (< 15 words)
        """
        word_count = len(sentence.split())
        if word_count < 15:
            raise ValueError(
                f"Sentence must have at least 15 words, got {word_count}"
            )
        self.sentences.append(sentence)
    
    def validate_sentence(self, sentence: str) -> Dict[str, any]:
        """
        Validate a sentence for experiments.
        
        Args:
            sentence: Sentence to validate
            
        Returns:
            Dictionary with validation results
        """
        words = sentence.split()
        word_count = len(words)
        
        return {
            'valid': word_count >= 15,
            'word_count': word_count,
            'char_count': len(sentence),
            'meets_minimum': word_count >= 15,
            'message': 'Valid' if word_count >= 15 else f'Too short: {word_count} words (minimum 15)'
        }
    
    def save_to_file(self, filepath: Path) -> None:
        """
        Save sentences to JSON file.
        
        Args:
            filepath: Path to save file
        """
        data = {
            'sentences': [
                {
                    'text': sentence,
                    'word_count': len(sentence.split())
                }
                for sentence in self.sentences
            ]
        }
        
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def load_from_file(self, filepath: Path) -> None:
        """
        Load sentences from JSON file.
        
        Args:
            filepath: Path to load from
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid
        """
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if 'sentences' not in data:
            raise ValueError("Invalid file format: missing 'sentences' key")
        
        self.sentences = []
        for item in data['sentences']:
            if isinstance(item, dict) and 'text' in item:
                self.sentences.append(item['text'])
            elif isinstance(item, str):
                self.sentences.append(item)
        
        invalid = [s for s in self.sentences if len(s.split()) < 15]
        if invalid:
            raise ValueError(
                f"Found {len(invalid)} sentences with less than 15 words"
            )
    
    def get_statistics(self) -> Dict[str, any]:
        """
        Get statistics about sentences.
        
        Returns:
            Dictionary with statistics
        """
        word_counts = [len(s.split()) for s in self.sentences]
        char_counts = [len(s) for s in self.sentences]
        
        return {
            'total_sentences': len(self.sentences),
            'word_count': {
                'min': min(word_counts) if word_counts else 0,
                'max': max(word_counts) if word_counts else 0,
                'avg': sum(word_counts) / len(word_counts) if word_counts else 0
            },
            'char_count': {
                'min': min(char_counts) if char_counts else 0,
                'max': max(char_counts) if char_counts else 0,
                'avg': sum(char_counts) / len(char_counts) if char_counts else 0
            }
        }

