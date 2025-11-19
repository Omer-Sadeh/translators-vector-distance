import os
import numpy as np
from typing import List, Union
from sentence_transformers import SentenceTransformer

os.environ['TOKENIZERS_PARALLELISM'] = 'false'


class EmbeddingEngine:
    """
    Vector embedding calculator using sentence-transformers.
    
    Uses all-MiniLM-L6-v2 model for generating sentence embeddings.
    This is a free, local model requiring no API key.
    """
    
    def __init__(
        self,
        model_name: str = 'all-MiniLM-L6-v2',
        device: str = 'cpu',
        batch_size: int = 32
    ):
        """
        Initialize embedding engine.
        
        Args:
            model_name: Name of sentence-transformers model
            device: Device to use ('cpu' or 'cuda')
            batch_size: Batch size for encoding
        """
        self.model_name = model_name
        self.device = device
        self.batch_size = batch_size
        self._model = None
        self._embedding_cache = {}
    
    @property
    def model(self) -> SentenceTransformer:
        """
        Lazy-load the model.
        
        Returns:
            SentenceTransformer model instance
        """
        if self._model is None:
            self._model = SentenceTransformer(self.model_name, device=self.device)
        return self._model
    
    def encode(
        self,
        texts: Union[str, List[str]],
        use_cache: bool = True,
        show_progress: bool = False
    ) -> np.ndarray:
        """
        Generate embeddings for text(s).
        
        Args:
            texts: Single text string or list of texts
            use_cache: Use cached embeddings if available
            show_progress: Show progress bar for batch encoding
            
        Returns:
            Numpy array of embeddings (shape: [n_texts, embedding_dim])
            For single text: shape is [1, embedding_dim]
        """
        is_single = isinstance(texts, str)
        if is_single:
            texts = [texts]
        
        if use_cache:
            cached_results = []
            texts_to_encode = []
            text_indices = []
            
            for i, text in enumerate(texts):
                if text in self._embedding_cache:
                    cached_results.append((i, self._embedding_cache[text]))
                else:
                    texts_to_encode.append(text)
                    text_indices.append(i)
            
            if not texts_to_encode:
                embeddings = np.array([emb for _, emb in sorted(cached_results)])
                return embeddings[0] if is_single else embeddings
            
            new_embeddings = self._encode_batch(texts_to_encode, show_progress)
            
            for text, embedding in zip(texts_to_encode, new_embeddings):
                self._embedding_cache[text] = embedding
            
            all_embeddings = np.zeros((len(texts), new_embeddings.shape[1]))
            for i, emb in cached_results:
                all_embeddings[i] = emb
            for i, emb in zip(text_indices, new_embeddings):
                all_embeddings[i] = emb
            
            return all_embeddings[0] if is_single else all_embeddings
        else:
            embeddings = self._encode_batch(texts, show_progress)
            return embeddings[0] if is_single else embeddings
    
    def _encode_batch(
        self,
        texts: List[str],
        show_progress: bool = False
    ) -> np.ndarray:
        """
        Encode a batch of texts.
        
        Args:
            texts: List of text strings
            show_progress: Show progress bar
            
        Returns:
            Numpy array of embeddings
        """
        embeddings = self.model.encode(
            texts,
            batch_size=self.batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        
        return embeddings
    
    def clear_cache(self) -> None:
        """Clear the embedding cache."""
        self._embedding_cache.clear()
    
    def get_cache_size(self) -> int:
        """
        Get number of cached embeddings.
        
        Returns:
            Number of entries in cache
        """
        return len(self._embedding_cache)
    
    def get_embedding_dimension(self) -> int:
        """
        Get embedding dimension of the model.
        
        Returns:
            Embedding dimension
        """
        return self.model.get_sentence_embedding_dimension()

