"""Tests for command handler."""

import pytest
from unittest.mock import Mock, AsyncMock
from pynostr.event import Event

from src.command_handler import CommandHandler


@pytest.fixture
def mock_agent():
    """Create a mock agent."""
    agent = Mock()
    agent.config_manager = Mock()
    agent.config_manager.get_agent_name = Mock(return_value="Test Agent")
    agent.config_manager.get_authorized_users = Mock(return_value=[])  # Empty = allow all (backward compat)
    agent.running = True
    agent.posting_interval = 60
    agent.last_post_time = "2024-01-01T00:00:00"
    agent.llm_provider = Mock()
    agent.llm_provider.set_system_prompt = Mock()
    agent.config_manager.update_system_prompt = Mock()
    agent.generate_and_post = AsyncMock()
    agent.set_posting_interval = Mock()
    return agent


@pytest.fixture
def mock_event():
    """Create a mock Nostr event."""
    event = Mock(spec=Event)
    event.pubkey = "test_pubkey_1234567890"
    return event


@pytest.mark.asyncio
async def test_command_handler_initialization(mock_agent):
    """Test command handler initialization."""
    handler = CommandHandler(mock_agent)
    assert handler.agent == mock_agent
    assert 'status' in handler.commands
    assert 'help' in handler.commands


@pytest.mark.asyncio
async def test_handle_status_command(mock_agent, mock_event):
    """Test status command."""
    handler = CommandHandler(mock_agent)
    
    response = await handler.handle_command("!status", "user_pubkey", mock_event)
    
    assert "Agent Status" in response
    assert "Test Agent" in response
    assert "Running" in response
    assert "60" in response


@pytest.mark.asyncio
async def test_handle_help_command(mock_agent, mock_event):
    """Test help command."""
    handler = CommandHandler(mock_agent)
    
    response = await handler.handle_command("!help", "user_pubkey", mock_event)
    
    assert "Available Commands" in response
    assert "!status" in response
    assert "!post-now" in response


@pytest.mark.asyncio
async def test_handle_set_prompt_command(mock_agent, mock_event):
    """Test set-prompt command."""
    handler = CommandHandler(mock_agent)
    
    response = await handler.handle_command(
        "!set-prompt New test prompt",
        "user_pubkey",
        mock_event
    )
    
    assert "updated successfully" in response.lower()
    mock_agent.llm_provider.set_system_prompt.assert_called_once_with("New test prompt")
    mock_agent.config_manager.update_system_prompt.assert_called_once_with("New test prompt")


@pytest.mark.asyncio
async def test_handle_set_prompt_empty(mock_agent, mock_event):
    """Test set-prompt command with empty prompt."""
    handler = CommandHandler(mock_agent)
    
    response = await handler.handle_command("!set-prompt", "user_pubkey", mock_event)
    
    assert "Usage" in response
    mock_agent.llm_provider.set_system_prompt.assert_not_called()


@pytest.mark.asyncio
async def test_handle_post_now_command(mock_agent, mock_event):
    """Test post-now command."""
    handler = CommandHandler(mock_agent)
    
    response = await handler.handle_command("!post-now", "user_pubkey", mock_event)
    
    assert "published successfully" in response.lower()
    mock_agent.generate_and_post.assert_called_once()


@pytest.mark.asyncio
async def test_handle_set_interval_command(mock_agent, mock_event):
    """Test set-interval command."""
    handler = CommandHandler(mock_agent)
    
    response = await handler.handle_command("!set-interval 30", "user_pubkey", mock_event)
    
    assert "30 minutes" in response
    mock_agent.set_posting_interval.assert_called_once_with(30)


@pytest.mark.asyncio
async def test_handle_set_interval_invalid(mock_agent, mock_event):
    """Test set-interval command with invalid input."""
    handler = CommandHandler(mock_agent)
    
    # Test with non-numeric value
    response = await handler.handle_command("!set-interval abc", "user_pubkey", mock_event)
    assert "Invalid interval" in response
    
    # Test with out of range value
    response = await handler.handle_command("!set-interval 2000", "user_pubkey", mock_event)
    assert "between 1 and 1440" in response
    
    # Test with empty value
    response = await handler.handle_command("!set-interval", "user_pubkey", mock_event)
    assert "Usage" in response


@pytest.mark.asyncio
async def test_handle_unknown_command(mock_agent, mock_event):
    """Test handling of unknown command."""
    handler = CommandHandler(mock_agent)
    
    response = await handler.handle_command("!unknown", "user_pubkey", mock_event)
    
    assert "Unknown command" in response
    assert "!help" in response


@pytest.mark.asyncio
async def test_handle_command_without_prefix(mock_agent, mock_event):
    """Test command handling without ! prefix."""
    handler = CommandHandler(mock_agent)
    
    response = await handler.handle_command("status", "user_pubkey", mock_event)
    
    assert "Agent Status" in response


@pytest.mark.asyncio
async def test_handle_command_error_handling(mock_agent, mock_event):
    """Test error handling in command execution."""
    handler = CommandHandler(mock_agent)
    
    # Make generate_and_post raise an error
    mock_agent.generate_and_post = AsyncMock(side_effect=Exception("Posting failed"))
    
    response = await handler.handle_command("!post-now", "user_pubkey", mock_event)
    
    assert "Error" in response
    assert "Posting failed" in response
