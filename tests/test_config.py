"""Tests for configuration manager."""

import pytest
import os
import tempfile
import yaml
from pathlib import Path
from src.config_manager import ConfigManager, Config


def test_config_defaults():
    """Test configuration with defaults."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create empty config file
        config_path = Path(tmpdir) / "agent.yaml"
        config_path.write_text("")
        
        # Set required env vars
        os.environ["NOSTR_NSEC"] = "nsec14htkwc05374nh2ke77g93ljpz6xtf88zh3nzgh0upjgxmglxeemszdnxvq"
        os.environ["OPENROUTER_API_KEY"] = "test_key"
        
        config = ConfigManager(str(config_path))
        
        assert config.config is not None
        assert config.get_agent_name() == "Shitposter Agent"
        assert config.get_posting_interval() == 60


def test_config_loading():
    """Test loading configuration from YAML."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "agent.yaml"
        config_data = {
            "agent": {
                "name": "Test Agent",
                "personality": "Test personality"
            },
            "posting": {
                "interval_minutes": 30
            }
        }
        config_path.write_text(yaml.dump(config_data))
        
        os.environ["NOSTR_NSEC"] = "nsec14htkwc05374nh2ke77g93ljpz6xtf88zh3nzgh0upjgxmglxeemszdnxvq"
        os.environ["OPENROUTER_API_KEY"] = "test_key"
        
        config = ConfigManager(str(config_path))
        
        assert config.get_agent_name() == "Test Agent"
        assert config.get_posting_interval() == 30
        assert "Test personality" in config.get_system_prompt()


def test_config_env_vars():
    """Test environment variable loading."""
    os.environ["NOSTR_NSEC"] = "nsec14htkwc05374nh2ke77g93ljpz6xtf88zh3nzgh0upjgxmglxeemszdnxvq"
    os.environ["OPENROUTER_API_KEY"] = "test_api_key"
    os.environ["NOSTR_RELAYS"] = "wss://relay1.com,wss://relay2.com"
    os.environ["LLM_MODEL_NAME"] = "test-model"
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "agent.yaml"
        config_path.write_text("")
        
        config = ConfigManager(str(config_path))
        
        assert config.get_private_key() == os.environ["NOSTR_NSEC"]
        assert config.get_api_key() == "test_api_key"
        assert len(config.get_relays()) == 2
        assert config.get_model_name() == "test-model"


def test_config_missing_env():
    """Test error when required env vars are missing."""
    # Remove required vars
    if "NOSTR_NSEC" in os.environ:
        del os.environ["NOSTR_NSEC"]
    if "OPENROUTER_API_KEY" in os.environ:
        del os.environ["OPENROUTER_API_KEY"]
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "agent.yaml"
        config_path.write_text("")
        
        config = ConfigManager(str(config_path))
        
        with pytest.raises(ValueError):
            config.get_private_key()
        
        with pytest.raises(ValueError):
            config.get_api_key()
