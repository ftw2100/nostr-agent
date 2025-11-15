"""Autonomous posting loop for the agent."""

import asyncio
import time
from datetime import datetime
from agentstr.logger import get_logger

from .constants import MIN_POSTING_INTERVAL_SECONDS

logger = get_logger(__name__)


class PostingLoop:
    """Manages the autonomous posting schedule."""
    
    def __init__(self, agent, interval_minutes: int = 60):
        """Initialize posting loop.
        
        Args:
            agent: Reference to the main agent instance.
            interval_minutes: Posting interval in minutes.
        """
        self.agent = agent
        self.interval_minutes = interval_minutes
        self.interval_seconds = interval_minutes * 60
        self.running = False
        self.last_post_time = None
        logger.info(f"Posting loop initialized with {interval_minutes} minute interval")
    
    def set_interval(self, minutes: int):
        """Update posting interval.
        
        Args:
            minutes: New interval in minutes.
            
        Raises:
            ValueError: If interval is below minimum allowed.
        """
        # Enforce minimum interval to prevent spam
        if minutes * 60 < MIN_POSTING_INTERVAL_SECONDS:
            raise ValueError(
                f"Posting interval must be at least {MIN_POSTING_INTERVAL_SECONDS} seconds "
                f"({MIN_POSTING_INTERVAL_SECONDS / 60:.1f} minutes) to prevent spam"
            )
        
        self.interval_minutes = minutes
        self.interval_seconds = minutes * 60
        logger.info(f"Posting interval updated to {minutes} minutes")
    
    async def run(self):
        """Run the posting loop continuously."""
        self.running = True
        logger.info("Starting posting loop...")
        
        while self.running:
            try:
                # Wait for the interval
                logger.info(f"Waiting {self.interval_minutes} minutes until next post...")
                await asyncio.sleep(self.interval_seconds)
                
                if not self.running:
                    break
                
                # Generate and post
                logger.info("Interval elapsed, generating and posting...")
                await self.agent.generate_and_post()
                self.last_post_time = datetime.now().isoformat()
                
            except asyncio.CancelledError:
                logger.info("Posting loop cancelled")
                raise  # Re-raise to allow proper cleanup
            except Exception as e:
                logger.error(f"Error in posting loop: {e}", exc_info=True)
                # Wait a bit before retrying on error
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    def stop(self):
        """Stop the posting loop."""
        self.running = False
        logger.info("Posting loop stopped")
