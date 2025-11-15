"""Circuit breaker pattern for resilient API calls."""

import time
from typing import Callable, Any
from agentstr.logger import get_logger

logger = get_logger(__name__)


class CircuitBreaker:
    """Circuit breaker to prevent cascading failures.
    
    States:
    - CLOSED: Normal operation, requests allowed
    - OPEN: Too many failures, requests blocked
    - HALF_OPEN: Testing if service recovered, limited requests allowed
    """
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60, half_open_max_calls: int = 1):
        """Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit.
            timeout: Seconds to wait before attempting half-open state.
            half_open_max_calls: Max calls allowed in half-open state.
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.half_open_max_calls = half_open_max_calls
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.half_open_calls = 0
        
        logger.info(
            f"Circuit breaker initialized: threshold={failure_threshold}, "
            f"timeout={timeout}s"
        )
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection.
        
        Args:
            func: Function to call.
            *args: Positional arguments for function.
            **kwargs: Keyword arguments for function.
            
        Returns:
            Function result.
            
        Raises:
            Exception: If circuit is open or function fails.
        """
        # Check circuit state
        if self.state == "OPEN":
            # Check if timeout has passed
            if time.time() - self.last_failure_time > self.timeout:
                logger.info("Circuit breaker: Moving to HALF_OPEN state")
                self.state = "HALF_OPEN"
                self.half_open_calls = 0
            else:
                raise Exception(
                    f"Circuit breaker is OPEN. Too many failures. "
                    f"Retry after {self.timeout - (time.time() - self.last_failure_time):.0f} seconds"
                )
        
        # Execute function
        try:
            result = func(*args, **kwargs)
            
            # Success - reset if in HALF_OPEN or CLOSED
            if self.state == "HALF_OPEN":
                logger.info("Circuit breaker: Service recovered, moving to CLOSED")
                self.state = "CLOSED"
                self.failure_count = 0
                self.half_open_calls = 0
            elif self.state == "CLOSED":
                # Reset failure count on success
                self.failure_count = 0
            
            return result
            
        except Exception as e:
            # Failure - increment counter
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            logger.warning(
                f"Circuit breaker: Failure {self.failure_count}/{self.failure_threshold} - {type(e).__name__}"
            )
            
            # Check if threshold exceeded
            if self.failure_count >= self.failure_threshold:
                logger.error(
                    f"Circuit breaker: Threshold exceeded, opening circuit. "
                    f"Will retry after {self.timeout}s"
                )
                self.state = "OPEN"
            
            # Re-raise the exception
            raise
    
    async def call_async(self, func: Callable, *args, **kwargs) -> Any:
        """Execute async function with circuit breaker protection.
        
        Args:
            func: Async function to call.
            *args: Positional arguments for function.
            **kwargs: Keyword arguments for function.
            
        Returns:
            Function result.
            
        Raises:
            Exception: If circuit is open or function fails.
        """
        # Check circuit state
        if self.state == "OPEN":
            # Check if timeout has passed
            if time.time() - self.last_failure_time > self.timeout:
                logger.info("Circuit breaker: Moving to HALF_OPEN state")
                self.state = "HALF_OPEN"
                self.half_open_calls = 0
            else:
                raise Exception(
                    f"Circuit breaker is OPEN. Too many failures. "
                    f"Retry after {self.timeout - (time.time() - self.last_failure_time):.0f} seconds"
                )
        
        # Check half-open call limit
        if self.state == "HALF_OPEN":
            if self.half_open_calls >= self.half_open_max_calls:
                raise Exception("Circuit breaker is HALF_OPEN, call limit reached")
            self.half_open_calls += 1
        
        # Execute function
        try:
            result = await func(*args, **kwargs)
            
            # Success - reset if in HALF_OPEN or CLOSED
            if self.state == "HALF_OPEN":
                logger.info("Circuit breaker: Service recovered, moving to CLOSED")
                self.state = "CLOSED"
                self.failure_count = 0
                self.half_open_calls = 0
            elif self.state == "CLOSED":
                # Reset failure count on success
                self.failure_count = 0
            
            return result
            
        except Exception as e:
            # Failure - increment counter
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            logger.warning(
                f"Circuit breaker: Failure {self.failure_count}/{self.failure_threshold} - {type(e).__name__}"
            )
            
            # Check if threshold exceeded
            if self.failure_count >= self.failure_threshold:
                logger.error(
                    f"Circuit breaker: Threshold exceeded, opening circuit. "
                    f"Will retry after {self.timeout}s"
                )
                self.state = "OPEN"
            
            # Re-raise the exception
            raise
    
    def reset(self):
        """Manually reset circuit breaker to CLOSED state."""
        logger.info("Circuit breaker manually reset")
        self.state = "CLOSED"
        self.failure_count = 0
        self.last_failure_time = None
        self.half_open_calls = 0
    
    def get_state(self) -> str:
        """Get current circuit breaker state."""
        return self.state
