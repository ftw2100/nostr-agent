"""Content deduplication to prevent posting similar content."""

from collections import deque
from hashlib import sha256
from agentstr.logger import get_logger

from .constants import MAX_CONTENT_HISTORY, CONTENT_SIMILARITY_THRESHOLD

logger = get_logger(__name__)


class ContentDeduplicator:
    """Prevents posting duplicate or very similar content."""
    
    def __init__(self, max_history: int = MAX_CONTENT_HISTORY, similarity_threshold: float = CONTENT_SIMILARITY_THRESHOLD):
        """Initialize content deduplicator.
        
        Args:
            max_history: Maximum number of content hashes to remember.
            similarity_threshold: Threshold for considering content similar (0.0-1.0).
        """
        self.history = deque(maxlen=max_history)
        self.similarity_threshold = similarity_threshold
        logger.info(f"Content deduplicator initialized with {max_history} item history")
    
    def is_duplicate(self, content: str) -> bool:
        """Check if content is duplicate or very similar to previous posts.
        
        Args:
            content: Content to check.
            
        Returns:
            True if content is duplicate/similar, False otherwise.
        """
        if not content or not content.strip():
            return False
        
        # Normalize content for comparison
        normalized = self._normalize_content(content)
        content_hash = sha256(normalized.encode('utf-8')).hexdigest()
        
        # Check exact match
        if content_hash in self.history:
            logger.warning(f"Exact duplicate content detected (hash: {content_hash[:16]}...)")
            return True
        
        # Check similarity (simple approach - can be enhanced with fuzzy matching)
        for stored_hash in self.history:
            # For now, we only check exact matches
            # Could enhance with Levenshtein distance or other similarity metrics
            pass
        
        # Add to history
        self.history.append(content_hash)
        return False
    
    def _normalize_content(self, content: str) -> str:
        """Normalize content for comparison.
        
        Args:
            content: Raw content.
            
        Returns:
            Normalized content.
        """
        # Lowercase, strip whitespace, remove extra spaces
        normalized = content.lower().strip()
        normalized = ' '.join(normalized.split())
        return normalized
    
    def clear(self):
        """Clear deduplication history."""
        self.history.clear()
        logger.info("Content deduplication history cleared")
