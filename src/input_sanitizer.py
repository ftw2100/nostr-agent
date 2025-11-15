"""Input sanitization utilities."""

import re
from agentstr.logger import get_logger

from .constants import MAX_INPUT_LENGTH, MAX_COMMAND_ARGS_LENGTH, MAX_GUIDANCE_LENGTH

logger = get_logger(__name__)


def sanitize_input(text: str, max_length: int = MAX_INPUT_LENGTH) -> str:
    """Sanitize user input to prevent injection attacks.
    
    Args:
        text: Raw input text.
        max_length: Maximum allowed length.
        
    Returns:
        Sanitized text.
    """
    if not text:
        return ""
    
    # Remove control characters (except newlines and tabs)
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    
    # Limit length
    if len(text) > max_length:
        logger.warning(f"Input truncated from {len(text)} to {max_length} characters")
        text = text[:max_length]
    
    return text.strip()


def sanitize_command_args(args: str, max_length: int = MAX_COMMAND_ARGS_LENGTH) -> str:
    """Sanitize command arguments specifically.
    
    Args:
        args: Command arguments.
        max_length: Maximum allowed length.
        
    Returns:
        Sanitized arguments.
    """
    return sanitize_input(args, max_length=max_length)
