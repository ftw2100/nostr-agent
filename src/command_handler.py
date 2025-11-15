"""Command handler for processing DM commands."""

import os
from pynostr.event import Event
from agentstr.logger import get_logger

from .input_sanitizer import sanitize_command_args
from .rate_limiter import RateLimiter
from .constants import (
    DEFAULT_COMMAND_RATE_LIMIT,
    RATE_LIMIT_WINDOW_MINUTES
)

logger = get_logger(__name__)


class CommandHandler:
    """Handles commands received via direct messages."""
    
    def __init__(self, agent):
        """Initialize command handler.
        
        Args:
            agent: Reference to the main agent instance.
        """
        self.agent = agent
        self.commands = {
            'status': self._handle_status,
            'set-prompt': self._handle_set_prompt,
            'post-now': self._handle_post_now,
            'set-interval': self._handle_set_interval,
            'help': self._handle_help,
        }
        # Initialize rate limiter
        self.rate_limiter = RateLimiter(
            max_requests=DEFAULT_COMMAND_RATE_LIMIT,
            window_minutes=RATE_LIMIT_WINDOW_MINUTES
        )
        logger.info("Command handler initialized")
    
    def _is_authorized(self, user: str) -> bool:
        """Check if user is authorized to use commands.
        
        Args:
            user: User's public key.
            
        Returns:
            True if authorized, False otherwise.
        """
        authorized_users = self.agent.config_manager.get_authorized_users()
        # If no authorized users specified, allow all (backward compatibility)
        if not authorized_users:
            return True
        return user in authorized_users
    
    async def handle_command(self, command: str, user: str, event: Event) -> str:
        """Parse and execute a command.
        
        Args:
            command: The command string (with or without ! prefix).
            user: User's public key.
            event: The Nostr event containing the command.
            
        Returns:
            Response message to send back to user.
        """
        # Check authorization (except for help and status commands)
        command_stripped = command.strip().lstrip('!')
        parts = command_stripped.split(' ', 1)
        cmd = parts[0].lower() if parts else ""
        
        # Help and status are always allowed
        if cmd not in ['help', 'status']:
            if not self._is_authorized(user):
                logger.warning(f"Unauthorized command attempt from {user[:10]}...")
                return "❌ Unauthorized. You are not authorized to use commands. Contact the bot administrator."
            
            # Check rate limit
            if not self.rate_limiter.is_allowed(user):
                logger.warning(f"Rate limit exceeded for user {user[:10]}...")
                return "❌ Rate limit exceeded. Please wait before sending more commands."
        
        # Remove ! prefix if present
        command = command.strip().lstrip('!')
        
        # Split command and arguments
        parts = command.split(' ', 1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else None
        
        # Sanitize arguments
        if args:
            args = sanitize_command_args(args)
        
        logger.info(f"Processing command: {cmd} from user {user[:10]}...")
        
        if cmd in self.commands:
            try:
                response = await self.commands[cmd](args, user, event)
                logger.info(f"Command {cmd} executed successfully")
                return response
            except Exception as e:
                logger.error(f"Error executing command {cmd}: {e}")
                return f"Error executing command: {str(e)}"
        else:
            return f"Unknown command: {cmd}. Use !help for available commands."
    
    async def _handle_status(self, args, user, event) -> str:
        """Return agent status.
        
        Returns:
            Status message.
        """
        status_lines = [
            "🤖 Agent Status",
            f"Name: {self.agent.config_manager.get_agent_name()}",
            f"Status: {'Running' if self.agent.running else 'Stopped'}",
            f"Posting Interval: {self.agent.posting_interval} minutes",
            f"Last Post: {self.agent.last_post_time or 'Never'}",
        ]
        return "\n".join(status_lines)
    
    async def _handle_set_prompt(self, args, user, event) -> str:
        """Update system prompt.
        
        Args:
            args: New prompt text.
            
        Returns:
            Confirmation message.
        """
        if not args or not args.strip():
            return "Usage: !set-prompt <new prompt text>"
        
        try:
            # Args are already sanitized in handle_command
            sanitized_prompt = args.strip()
            self.agent.llm_provider.set_system_prompt(sanitized_prompt)
            self.agent.config_manager.update_system_prompt(sanitized_prompt)
            return "✅ System prompt updated successfully!"
        except Exception as e:
            return f"❌ Error updating prompt: {str(e)}"
    
    async def _handle_post_now(self, args, user, event) -> str:
        """Force immediate post.
        
        Returns:
            Confirmation message.
        """
        try:
            logger.info("Forcing immediate post via command")
            await self.agent.generate_and_post()
            return "✅ Post published successfully!"
        except Exception as e:
            logger.error(f"Error posting: {e}")
            return f"❌ Error posting: {str(e)}"
    
    async def _handle_set_interval(self, args, user, event) -> str:
        """Change posting interval.
        
        Args:
            args: New interval in minutes.
            
        Returns:
            Confirmation message.
        """
        if not args:
            return "Usage: !set-interval <minutes>"
        
        try:
            minutes = int(args.strip())
            # Minimum is 1 minute (60 seconds), but posting loop enforces 30 seconds minimum
            # So we allow 1 minute here, but posting loop will enforce its own minimum
            if minutes < 1 or minutes > 1440:
                return "❌ Interval must be between 1 and 1440 minutes"
            
            self.agent.set_posting_interval(minutes)
            return f"✅ Posting interval set to {minutes} minutes"
        except ValueError as e:
            if "must be at least" in str(e):
                return f"❌ {str(e)}"
            return "❌ Invalid interval. Please provide a number."
        except Exception as e:
            return f"❌ Error setting interval: {str(e)}"
    
    async def _handle_help(self, args, user, event) -> str:
        """Show help message.
        
        Returns:
            Help text with available commands.
        """
        help_lines = [
            "📚 Available Commands:",
            "",
            "!status - Show agent status",
            "!set-prompt <text> - Update system prompt",
            "!post-now - Force immediate post",
            "!set-interval <minutes> - Change posting interval",
            "!help - Show this help message",
            "",
            "💡 You can also send regular messages as guidance for the next post!",
        ]
        return "\n".join(help_lines)
