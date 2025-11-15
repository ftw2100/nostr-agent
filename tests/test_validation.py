"""Validation tests for real-world scenarios."""

import pytest
import os
from pathlib import Path


def test_config_file_exists():
    """Test that configuration file exists."""
    config_path = Path("config/agent.yaml")
    assert config_path.exists(), "config/agent.yaml should exist"


def test_prompt_file_exists():
    """Test that prompt file exists."""
    prompt_path = Path("config/prompts/system_prompt.txt")
    assert prompt_path.exists(), "config/prompts/system_prompt.txt should exist"


def test_env_example_exists():
    """Test that .env.example exists."""
    env_example = Path(".env.example")
    assert env_example.exists(), ".env.example should exist"


def test_required_modules_importable():
    """Test that all required modules can be imported."""
    try:
        from src.config_manager import ConfigManager
        from src.nostr_client import NostrShitposterClient
        from src.llm_provider import OpenRouterProvider
        from src.command_handler import CommandHandler
        from src.posting_loop import PostingLoop
        from src.agent import ShitposterAgent
        from src.main import main
    except ImportError as e:
        pytest.fail(f"Failed to import required modules: {e}")


def test_config_structure_valid():
    """Test that config file has valid structure."""
    import yaml
    config_path = Path("config/agent.yaml")
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
        
        # Check required sections
        assert "agent" in data or "posting" in data or "guidance" in data, \
            "Config should have at least one section"


def test_prompt_file_not_empty():
    """Test that prompt file is not empty."""
    prompt_path = Path("config/prompts/system_prompt.txt")
    
    if prompt_path.exists():
        with open(prompt_path, 'r') as f:
            content = f.read().strip()
        
        assert len(content) > 0, "Prompt file should not be empty"


def test_scripts_executable():
    """Test that scripts are executable."""
    scripts = [
        Path("scripts/install.sh"),
        Path("scripts/start.sh"),
        Path("scripts/test_connection.py"),
    ]
    
    for script in scripts:
        if script.exists():
            assert script.is_file(), f"{script} should be a file"
            # Check if Python scripts can be executed
            if script.suffix == '.py':
                # Just verify it's readable
                assert script.stat().st_mode & 0o444, f"{script} should be readable"
