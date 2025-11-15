"""Integration tests for the agent."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pynostr.event import Event

from src.agent import ShitposterAgent
from src.config_manager import ConfigManager


@pytest.fixture
def mock_config_manager():
    """Create a mock config manager."""
    config = Mock(spec=ConfigManager)
    config.get_relays = Mock(return_value=["wss://relay.damus.io"])
    config.get_private_key = Mock(return_value="nsec14htkwc05374nh2ke77g93ljpz6xtf88zh3nzgh0upjgxmglxeemszdnxvq")
    config.get_model_name = Mock(return_value="openai/gpt-4o-mini")
    config.get_api_key = Mock(return_value="test_api_key")
    config.get_base_url = Mock(return_value="https://openrouter.ai/api/v1")
    config.get_system_prompt = Mock(return_value="You are a test agent.")
    config.get_posting_interval = Mock(return_value=60)
    config.get_agent_name = Mock(return_value="Test Agent")
    config.is_guidance_enabled = Mock(return_value=True)
    config.are_commands_enabled = Mock(return_value=True)
    config.get_authorized_users = Mock(return_value=[])  # Empty = allow all
    config.update_system_prompt = Mock()
    return config


@pytest.fixture
def mock_nostr_client():
    """Create a mock Nostr client."""
    client = Mock()
    client.publish_note = AsyncMock()
    client.listen_for_guidance = AsyncMock()
    client.send_dm = AsyncMock()
    client.update_metadata = AsyncMock()
    return client


@pytest.fixture
def mock_llm_provider():
    """Create a mock LLM provider."""
    provider = Mock()
    provider.set_system_prompt = Mock()
    provider.generate_content = AsyncMock(return_value="Generated test content")
    provider.generate_with_guidance = AsyncMock(return_value="Generated content with guidance")
    return provider


@pytest.mark.asyncio
async def test_agent_initialization(mock_config_manager, mock_nostr_client, mock_llm_provider):
    """Test agent initialization."""
    with patch('src.agent.ConfigManager', return_value=mock_config_manager), \
         patch('src.agent.NostrShitposterClient', return_value=mock_nostr_client), \
         patch('src.agent.OpenRouterProvider', return_value=mock_llm_provider), \
         patch('src.agent.CommandHandler'), \
         patch('src.agent.PostingLoop'), \
         patch('src.agent.RateLimiter'), \
         patch('src.agent.ContentDeduplicator'):
        
        agent = ShitposterAgent()
        
        assert agent.config_manager == mock_config_manager
        assert agent.nostr_client == mock_nostr_client
        assert agent.llm_provider == mock_llm_provider
        assert agent.running == False


@pytest.mark.asyncio
async def test_generate_and_post_success(mock_config_manager, mock_nostr_client, mock_llm_provider):
    """Test successful content generation and posting."""
    mock_event = Mock(spec=Event)
    mock_event.id = "test_event_id"
    mock_nostr_client.publish_note = AsyncMock(return_value=mock_event)
    
    with patch('src.agent.ConfigManager', return_value=mock_config_manager), \
         patch('src.agent.NostrShitposterClient', return_value=mock_nostr_client), \
         patch('src.agent.OpenRouterProvider', return_value=mock_llm_provider), \
         patch('src.agent.CommandHandler'), \
         patch('src.agent.PostingLoop'), \
         patch('src.agent.RateLimiter'), \
         patch('src.agent.ContentDeduplicator') as mock_dedup:
        
        # Mock deduplicator to not find duplicates
        mock_dedup_instance = Mock()
        mock_dedup_instance.is_duplicate = Mock(return_value=False)
        mock_dedup.return_value = mock_dedup_instance
        
        agent = ShitposterAgent()
        result = await agent.generate_and_post()
        
        assert result == mock_event
        mock_llm_provider.generate_content.assert_called_once()
        mock_nostr_client.publish_note.assert_called_once()


@pytest.mark.asyncio
async def test_generate_and_post_with_content(mock_config_manager, mock_nostr_client, mock_llm_provider):
    """Test posting with pre-generated content."""
    mock_event = Mock(spec=Event)
    mock_event.id = "test_event_id"
    mock_nostr_client.publish_note = AsyncMock(return_value=mock_event)
    
    with patch('src.agent.ConfigManager', return_value=mock_config_manager), \
         patch('src.agent.NostrShitposterClient', return_value=mock_nostr_client), \
         patch('src.agent.OpenRouterProvider', return_value=mock_llm_provider), \
         patch('src.agent.CommandHandler'), \
         patch('src.agent.PostingLoop'), \
         patch('src.agent.RateLimiter'), \
         patch('src.agent.ContentDeduplicator') as mock_dedup:
        
        # Mock deduplicator to not find duplicates
        mock_dedup_instance = Mock()
        mock_dedup_instance.is_duplicate = Mock(return_value=False)
        mock_dedup.return_value = mock_dedup_instance
        
        agent = ShitposterAgent()
        result = await agent.generate_and_post("Pre-generated content")
        
        assert result == mock_event
        mock_llm_provider.generate_content.assert_not_called()
        mock_nostr_client.publish_note.assert_called_once_with("Pre-generated content")


@pytest.mark.asyncio
async def test_handle_guidance_command(mock_config_manager, mock_nostr_client, mock_llm_provider):
    """Test handling guidance as a command."""
    mock_event = Mock(spec=Event)
    mock_event.pubkey = "test_pubkey"
    
    with patch('src.agent.ConfigManager', return_value=mock_config_manager), \
         patch('src.agent.NostrShitposterClient', return_value=mock_nostr_client), \
         patch('src.agent.OpenRouterProvider', return_value=mock_llm_provider), \
         patch('src.agent.CommandHandler') as mock_handler_class, \
         patch('src.agent.PostingLoop'), \
         patch('src.agent.RateLimiter') as mock_rate_limiter, \
         patch('src.agent.ContentDeduplicator'):
        
        # Mock rate limiter to allow requests
        mock_rate_limiter_instance = Mock()
        mock_rate_limiter_instance.is_allowed = Mock(return_value=True)
        mock_rate_limiter.return_value = mock_rate_limiter_instance
        
        mock_handler = Mock()
        mock_handler.handle_command = AsyncMock(return_value="Command response")
        mock_handler_class.return_value = mock_handler
        
        agent = ShitposterAgent()
        await agent._handle_guidance(mock_event, "!status")
        
        mock_handler.handle_command.assert_called_once()
        mock_nostr_client.send_dm.assert_called_once()


@pytest.mark.asyncio
async def test_handle_guidance_regular_message(mock_config_manager, mock_nostr_client, mock_llm_provider):
    """Test handling guidance as a regular message."""
    mock_event = Mock(spec=Event)
    mock_event.pubkey = "test_pubkey"
    mock_published_event = Mock(spec=Event)
    mock_published_event.id = "published_id"
    mock_nostr_client.publish_note = AsyncMock(return_value=mock_published_event)
    
    with patch('src.agent.ConfigManager', return_value=mock_config_manager), \
         patch('src.agent.NostrShitposterClient', return_value=mock_nostr_client), \
         patch('src.agent.OpenRouterProvider', return_value=mock_llm_provider), \
         patch('src.agent.CommandHandler'), \
         patch('src.agent.PostingLoop'), \
         patch('src.agent.RateLimiter') as mock_rate_limiter, \
         patch('src.agent.ContentDeduplicator') as mock_dedup:
        
        # Mock rate limiter to allow requests
        mock_rate_limiter_instance = Mock()
        mock_rate_limiter_instance.is_allowed = Mock(return_value=True)
        mock_rate_limiter.return_value = mock_rate_limiter_instance
        
        # Mock deduplicator to not find duplicates
        mock_dedup_instance = Mock()
        mock_dedup_instance.is_duplicate = Mock(return_value=False)
        mock_dedup.return_value = mock_dedup_instance
        
        agent = ShitposterAgent()
        await agent._handle_guidance(mock_event, "Make a post about Bitcoin")
        
        mock_llm_provider.generate_with_guidance.assert_called_once()
        mock_nostr_client.publish_note.assert_called_once()
        assert mock_nostr_client.send_dm.call_count == 1  # Confirmation message


@pytest.mark.asyncio
async def test_set_posting_interval(mock_config_manager, mock_nostr_client, mock_llm_provider):
    """Test setting posting interval."""
    with patch('src.agent.ConfigManager', return_value=mock_config_manager), \
         patch('src.agent.NostrShitposterClient', return_value=mock_nostr_client), \
         patch('src.agent.OpenRouterProvider', return_value=mock_llm_provider), \
         patch('src.agent.CommandHandler'), \
         patch('src.agent.PostingLoop') as mock_loop_class, \
         patch('src.agent.RateLimiter'), \
         patch('src.agent.ContentDeduplicator'):
        
        mock_loop = Mock()
        mock_loop.set_interval = Mock()
        mock_loop_class.return_value = mock_loop
        
        agent = ShitposterAgent()
        agent.set_posting_interval(30)
        
        assert agent.posting_interval == 30
        mock_loop.set_interval.assert_called_once_with(30)
