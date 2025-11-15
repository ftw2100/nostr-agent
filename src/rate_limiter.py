"""Rate limiting utility for preventing abuse."""

from collections import defaultdict
from datetime import datetime, timedelta
from agentstr.logger import get_logger

from .constants import RATE_LIMIT_WINDOW_MINUTES

logger = get_logger(__name__)


class RateLimiter:
    """Rate limiter to prevent abuse of commands and guidance."""
    
    def __init__(self, max_requests: int = 10, window_minutes: int = 60):
        """Initialize rate limiter.
        
        Args:
            max_requests: Maximum number of requests allowed in the window.
            window_minutes: Time window in minutes.
        """
        self.max_requests = max_requests
        self.window = timedelta(minutes=window_minutes)
        self.requests = defaultdict(list)
        logger.info(f"Rate limiter initialized: {max_requests} requests per {window_minutes} minutes")
    
    def is_allowed(self, user: str) -> bool:
        """Check if a user is allowed to make a request.
        
        Args:
            user: User identifier (public key).
            
        Returns:
            True if request is allowed, False if rate limited.
        """
        now = datetime.now()
        user_requests = self.requests[user]
        
        # Remove old requests outside the window
        user_requests[:] = [
            req_time for req_time in user_requests 
            if now - req_time < self.window
        ]
        
        # Check if limit exceeded
        if len(user_requests) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for user {user[:10]}... ({len(user_requests)}/{self.max_requests})")
            return False
        
        # Add current request
        user_requests.append(now)
        return True
    
    def reset(self, user: str = None):
        """Reset rate limit for a user or all users.
        
        Args:
            user: User identifier. If None, resets all users.
        """
        if user:
            self.requests[user] = []
            logger.info(f"Rate limit reset for user {user[:10]}...")
        else:
            self.requests.clear()
            logger.info("Rate limit reset for all users")
