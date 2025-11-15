"""Configuration management for the Nostr Shitposter Agent."""

import os
import yaml
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from agentstr.logger import get_logger

logger = get_logger(__name__)


class PostingConfig(BaseModel):
    """Posting configuration."""
    interval_minutes: int = Field(default=60, ge=1, le=1440)
    min_interval: int = Field(default=30, ge=1)
    max_interval: int = Field(default=120, ge=1)


class GuidanceConfig(BaseModel):
    """Guidance/command configuration."""
    enabled: bool = True
    commands_enabled: bool = True


class AgentConfig(BaseModel):
    """Agent configuration."""
    name: str = "Shitposter Agent"
    personality: str = "You are a witty Nostr shitposter."


class Config(BaseModel):
    """Main configuration model."""
    agent: AgentConfig = Field(default_factory=AgentConfig)
    posting: PostingConfig = Field(default_factory=PostingConfig)
    guidance: GuidanceConfig = Field(default_factory=GuidanceConfig)


class ConfigManager:
    """Manages configuration loading and access."""
    
    def __init__(self, config_path: str = "config/agent.yaml"):
        """Initialize configuration manager.
        
        Args:
            config_path: Path to YAML configuration file.
        """
        # Load environment variables
        load_dotenv()
        
        self.config_path = Path(config_path)
        self.config: Optional[Config] = None
        self._load_config()
    
    def _load_config(self):
        """Load configuration from YAML file."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                data = yaml.safe_load(f) or {}
            self.config = Config(**data)
        else:
            # Use defaults
            self.config = Config()
    
    def get_relays(self) -> List[str]:
        """Get list of Nostr relay URLs."""
        relays_env = os.getenv("NOSTR_RELAYS", "")
        if relays_env:
            return [r.strip() for r in relays_env.split(",") if r.strip()]
        return ["wss://relay.damus.io", "wss://nostr-pub.wellorder.net"]
    
    def get_private_key(self) -> str:
        """Get Nostr private key (nsec format)."""
        nsec = os.getenv("NOSTR_NSEC")
        if not nsec:
            raise ValueError("NOSTR_NSEC environment variable is required")
        return nsec
    
    def get_api_key(self) -> str:
        """Get OpenRouter API key."""
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is required")
        return api_key
    
    def get_model_name(self) -> str:
        """Get LLM model name."""
        return os.getenv("LLM_MODEL_NAME", "openai/gpt-4o-mini")
    
    def get_base_url(self) -> str:
        """Get LLM base URL."""
        return os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")
    
    def get_system_prompt(self) -> str:
        """Get system prompt from config or file."""
        if self.config and self.config.agent.personality:
            return self.config.agent.personality
        
        # Try to load from prompts file
        prompt_path = Path("config/prompts/system_prompt.txt")
        if prompt_path.exists():
            with open(prompt_path, 'r') as f:
                return f.read().strip()
        
        return "You are a witty Nostr shitposter."
    
    def get_posting_interval(self) -> int:
        """Get posting interval in minutes."""
        if self.config:
            return self.config.posting.interval_minutes
        return int(os.getenv("POSTING_INTERVAL_MINUTES", "60"))
    
    def get_agent_name(self) -> str:
        """Get agent name."""
        if self.config:
            return self.config.agent.name
        return "Shitposter Agent"
    
    def update_system_prompt(self, prompt: str):
        """Update system prompt dynamically."""
        if self.config:
            self.config.agent.personality = prompt
    
    def is_guidance_enabled(self) -> bool:
        """Check if guidance is enabled."""
        if self.config:
            return self.config.guidance.enabled
        return True
    
    def are_commands_enabled(self) -> bool:
        """Check if commands are enabled."""
        if self.config:
            return self.config.guidance.commands_enabled
        return True
    
    def get_authorized_users(self) -> list[str]:
        """Get list of authorized user public keys for commands.
        
        Returns:
            List of authorized public keys (hex or bech32 format).
        """
        authorized_env = os.getenv("AUTHORIZED_PUBKEYS", "")
        if authorized_env:
            # Split by comma and clean up
            users = [u.strip() for u in authorized_env.split(",") if u.strip()]
            return users
        # If no authorized users specified, allow all (backward compatibility)
        # But log a warning
        logger.warning("No AUTHORIZED_PUBKEYS set - all users can use commands (security risk)")
        return []
