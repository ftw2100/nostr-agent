"""Main agent class that orchestrates all components."""

import asyncio
from datetime import datetime
from typing import Optional
from agentstr.logger import get_logger

from .config_manager import ConfigManager
from .nostr_client import NostrShitposterClient
from .llm_provider import OpenRouterProvider
from .command_handler import CommandHandler
from .posting_loop import PostingLoop
from .rate_limiter import RateLimiter
from .content_deduplicator import ContentDeduplicator
from .input_sanitizer import sanitize_input
from .constants import (
    DEFAULT_COMMAND_RATE_LIMIT,
    DEFAULT_GUIDANCE_RATE_LIMIT,
    RATE_LIMIT_WINDOW_MINUTES,
    MAX_GUIDANCE_LENGTH
)

logger = get_logger(__name__)


class ShitposterAgent:
    """Main agent class for autonomous Nostr posting."""
    
    def __init__(self, config_path: str = "config/agent.yaml"):
        """Initialize the agent.
        
        Args:
            config_path: Path to configuration YAML file.
        """
        logger.info("Initializing Nostr Shitposter Agent...")
        
        # Initialize configuration
        self.config_manager = ConfigManager(config_path)
        
        # Initialize Nostr client
        self.nostr_client = NostrShitposterClient(
            relays=self.config_manager.get_relays(),
            private_key=self.config_manager.get_private_key()
        )
        
        # Initialize LLM provider
        self.llm_provider = OpenRouterProvider(
            model_name=self.config_manager.get_model_name(),
            api_key=self.config_manager.get_api_key(),
            base_url=self.config_manager.get_base_url()
        )
        
        # Set system prompt
        system_prompt = self.config_manager.get_system_prompt()
        self.llm_provider.set_system_prompt(system_prompt)
        
        # Initialize command handler
        self.command_handler = CommandHandler(self)
        
        # Initialize posting loop
        posting_interval = self.config_manager.get_posting_interval()
        self.posting_loop = PostingLoop(self, interval_minutes=posting_interval)
        self.posting_interval = posting_interval
        
        # Initialize rate limiter for guidance messages
        self.guidance_rate_limiter = RateLimiter(
            max_requests=DEFAULT_GUIDANCE_RATE_LIMIT,
            window_minutes=RATE_LIMIT_WINDOW_MINUTES
        )
        
        # Initialize content deduplicator
        self.content_deduplicator = ContentDeduplicator()
        
        # Agent state
        self.running = False
        self.last_post_time = None
        self.start_time = None
        
        logger.info("Agent initialized successfully")
    
    async def start(self):
        """Start the agent."""
        if self.running:
            logger.warning("Agent is already running")
            return
        
        logger.info("Starting agent...")
        self.running = True
        self.start_time = datetime.now()
        
        # Update Nostr metadata
        try:
            await self.nostr_client.update_metadata(
                name=self.config_manager.get_agent_name(),
                about="Autonomous Nostr shitposter agent powered by AI"
            )
        except Exception as e:
            logger.warning(f"Failed to update metadata: {e}")
        
        # Start guidance listener if enabled
        if self.config_manager.is_guidance_enabled():
            logger.info("Starting guidance listener...")
            guidance_task = asyncio.create_task(
                self.nostr_client.listen_for_guidance(self._handle_guidance)
            )
        else:
            guidance_task = None
        
        # Start posting loop
        logger.info("Starting posting loop...")
        posting_task = asyncio.create_task(self.posting_loop.run())
        
        # Wait for tasks (they run indefinitely)
        try:
            tasks = [posting_task]
            if guidance_task:
                tasks.append(guidance_task)
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, shutting down...")
            await self.stop()
        except Exception as e:
            logger.error(f"Error in agent loop: {e}", exc_info=True)
            await self.stop()
    
    async def stop(self):
        """Stop the agent."""
        logger.info("Stopping agent...")
        self.running = False
        self.posting_loop.stop()
        logger.info("Agent stopped")
    
    async def _handle_guidance(self, event, message: str):
        """Handle incoming guidance messages.
        
        Args:
            event: The Nostr event containing the message.
            message: The decrypted message content.
        """
        logger.info(f"Received guidance message from {event.pubkey[:10]}...")
        
        # Sanitize input
        message = sanitize_input(message, max_length=MAX_GUIDANCE_LENGTH)
        
        # Check if it's a command
        if message.startswith('!') and self.config_manager.are_commands_enabled():
            response = await self.command_handler.handle_command(
                message, event.pubkey, event
            )
            try:
                await self.nostr_client.send_dm(event.pubkey, response)
            except Exception as e:
                logger.error(f"Failed to send command response: {e}")
        else:
            # Treat as guidance for next post
            # Check rate limit for guidance
            if not self.guidance_rate_limiter.is_allowed(event.pubkey):
                logger.warning(f"Rate limit exceeded for guidance from {event.pubkey[:10]}...")
                try:
                    await self.nostr_client.send_dm(
                        event.pubkey,
                        "❌ Rate limit exceeded. Please wait before sending more guidance."
                    )
                except:
                    pass
                return
            
            try:
                logger.info("Generating post with user guidance...")
                content = await self.llm_provider.generate_with_guidance(message)
                await self.generate_and_post(content)
                
                # Send confirmation
                confirmation = (
                    f"✅ Post generated with your guidance!\n\n"
                    f"{content[:200]}{'...' if len(content) > 200 else ''}"
                )
                await self.nostr_client.send_dm(event.pubkey, confirmation)
            except Exception as e:
                logger.error(f"Error handling guidance: {e}")
                error_msg = f"❌ Error generating post: {str(e)}"
                try:
                    await self.nostr_client.send_dm(event.pubkey, error_msg)
                except:
                    pass
    
    async def generate_and_post(self, content: Optional[str] = None):
        """Generate content and post it to Nostr.
        
        Args:
            content: Optional pre-generated content. If None, generates new content.
            
        Returns:
            The published Event.
        """
        try:
            # Generate content if not provided
            if not content:
                logger.info("Generating new content...")
                content = await self.llm_provider.generate_content()
            
            # Validate content
            if not content or not content.strip():
                raise ValueError("Generated content is empty")
            
            # Check for duplicates
            if self.content_deduplicator.is_duplicate(content):
                logger.warning("Duplicate content detected, regenerating...")
                # Regenerate if duplicate
                content = await self.llm_provider.generate_content()
                # Check again (but allow if still duplicate to avoid infinite loop)
                if self.content_deduplicator.is_duplicate(content):
                    logger.warning("Still duplicate after regeneration, posting anyway")
            
            # Publish to Nostr
            logger.info(f"Publishing content ({len(content)} chars)...")
            event = await self.nostr_client.publish_note(content)
            
            self.last_post_time = datetime.now().isoformat()
            logger.info(f"Successfully posted: {event.id[:10]}...")
            logger.debug(f"Content: {content[:100]}...")
            
            return event
            
        except Exception as e:
            logger.error(f"Error generating/posting: {e}", exc_info=True)
            raise
    
    def set_posting_interval(self, minutes: int):
        """Update posting interval.
        
        Args:
            minutes: New interval in minutes.
        """
        self.posting_interval = minutes
        self.posting_loop.set_interval(minutes)
        logger.info(f"Posting interval updated to {minutes} minutes")
