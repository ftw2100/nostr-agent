"""End-to-end tests for the complete agent system."""

import pytest
import asyncio
import os
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path

from src.agent import ShitposterAgent


@pytest.fixture
def test_env_vars():
    """Set up test environment variables."""
    os.environ["NOSTR_NSEC"] = "nsec14htkwc05374nh2ke77g93ljpz6xtf88zh3nzgh0upjgxmglxeemszdnxvq"
    os.environ["OPENROUTER_API_KEY"] = "test_api_key"
    os.environ["LLM_MODEL_NAME"] = "openai/gpt-4o-mini"
    os.environ["LLM_BASE_URL"] = "https://openrouter.ai/api/v1"
    yield
    # Cleanup
    for key in ["NOSTR_NSEC", "OPENROUTER_API_KEY", "LLM_MODEL_NAME", "LLM_BASE_URL"]:
        if key in os.environ:
            del os.environ[key]


@pytest.mark.asyncio
async def test_agent_full_initialization(test_env_vars):
    """Test complete agent initialization with all components."""
    with patch('src.agent.NostrShitposterClient') as mock_nostr, \
         patch('src.agent.OpenRouterProvider') as mock_llm, \
         patch('src.agent.CommandHandler') as mock_cmd, \
         patch('src.agent.PostingLoop') as mock_loop, \
         patch('src.agent.RateLimiter'), \
         patch('src.agent.ContentDeduplicator'):
        
        # Setup mocks
        mock_nostr_instance = Mock()
        mock_nostr_instance.update_metadata = AsyncMock()
        mock_nostr_instance.listen_for_guidance = AsyncMock()
        mock_nostr.return_value = mock_nostr_instance
        
        mock_llm_instance = Mock()
        mock_llm_instance.set_system_prompt = Mock()
        mock_llm.return_value = mock_llm_instance
        
        mock_loop_instance = Mock()
        mock_loop_instance.run = AsyncMock()
        mock_loop.return_value = mock_loop_instance
        
        # Create agent
        agent = ShitposterAgent()
        
        # Verify all components initialized
        assert agent.config_manager is not None
        assert agent.nostr_client == mock_nostr_instance
        assert agent.llm_provider == mock_llm_instance
        assert agent.command_handler is not None
        assert agent.posting_loop == mock_loop_instance
        
        # Verify system prompt was set
        mock_llm_instance.set_system_prompt.assert_called_once()


@pytest.mark.asyncio
async def test_agent_start_sequence(test_env_vars):
    """Test agent start sequence."""
    with patch('src.agent.NostrShitposterClient') as mock_nostr, \
         patch('src.agent.OpenRouterProvider') as mock_llm, \
         patch('src.agent.CommandHandler'), \
         patch('src.agent.PostingLoop') as mock_loop:
        
        # Setup mocks
        mock_nostr_instance = Mock()
        mock_nostr_instance.update_metadata = AsyncMock()
        mock_nostr_instance.listen_for_guidance = AsyncMock()
        mock_nostr.return_value = mock_nostr_instance
        
        mock_llm_instance = Mock()
        mock_llm_instance.set_system_prompt = Mock()
        mock_llm.return_value = mock_llm_instance
        
        mock_loop_instance = Mock()
        mock_loop_instance.run = AsyncMock()
        mock_loop.return_value = mock_loop_instance
        
        agent = ShitposterAgent()
        
        # Create a task that will be cancelled
        async def start_and_cancel():
            task = asyncio.create_task(agent.start())
            await asyncio.sleep(0.1)
            await agent.stop()
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        await start_and_cancel()
        
        # Verify metadata was updated
        mock_nostr_instance.update_metadata.assert_called_once()
        # Verify guidance listener was started
        mock_nostr_instance.listen_for_guidance.assert_called_once()


@pytest.mark.asyncio
async def test_complete_posting_flow(test_env_vars):
    """Test complete posting flow from generation to publication."""
    with patch('src.agent.NostrShitposterClient') as mock_nostr, \
         patch('src.agent.OpenRouterProvider') as mock_llm, \
         patch('src.agent.CommandHandler'), \
         patch('src.agent.PostingLoop'), \
         patch('src.agent.RateLimiter'), \
         patch('src.agent.ContentDeduplicator') as mock_dedup:
        
        # Setup mocks
        mock_nostr_instance = Mock()
        mock_event = Mock()
        mock_event.id = "test_event_123"
        mock_nostr_instance.publish_note = AsyncMock(return_value=mock_event)
        mock_nostr.return_value = mock_nostr_instance
        
        mock_llm_instance = Mock()
        mock_llm_instance.set_system_prompt = Mock()
        mock_llm_instance.generate_content = AsyncMock(return_value="Generated test content")
        mock_llm.return_value = mock_llm_instance
        
        # Mock deduplicator
        mock_dedup_instance = Mock()
        mock_dedup_instance.is_duplicate = Mock(return_value=False)
        mock_dedup.return_value = mock_dedup_instance
        
        agent = ShitposterAgent()
        
        # Generate and post
        result = await agent.generate_and_post()
        
        # Verify flow
        assert result == mock_event
        mock_llm_instance.generate_content.assert_called_once()
        mock_nostr_instance.publish_note.assert_called_once_with("Generated test content")
        assert agent.last_post_time is not None


@pytest.mark.asyncio
async def test_command_flow_end_to_end(test_env_vars):
    """Test complete command flow from DM to response."""
    from pynostr.event import Event
    
    with patch('src.agent.NostrShitposterClient') as mock_nostr, \
         patch('src.agent.OpenRouterProvider') as mock_llm, \
         patch('src.agent.CommandHandler') as mock_cmd_class, \
         patch('src.agent.PostingLoop'), \
         patch('src.agent.RateLimiter') as mock_rate_limiter, \
         patch('src.agent.ContentDeduplicator'):
        
        # Setup mocks
        mock_nostr_instance = Mock()
        mock_nostr_instance.send_dm = AsyncMock()
        mock_nostr.return_value = mock_nostr_instance
        
        mock_llm_instance = Mock()
        mock_llm_instance.set_system_prompt = Mock()
        mock_llm.return_value = mock_llm_instance
        
        # Mock rate limiter
        mock_rate_limiter_instance = Mock()
        mock_rate_limiter_instance.is_allowed = Mock(return_value=True)
        mock_rate_limiter.return_value = mock_rate_limiter_instance
        
        # Setup command handler mock
        mock_cmd_instance = Mock()
        mock_cmd_instance.handle_command = AsyncMock(return_value="Status response")
        mock_cmd_class.return_value = mock_cmd_instance
        
        agent = ShitposterAgent()
        
        # Simulate receiving a command DM
        mock_event = Mock(spec=Event)
        mock_event.pubkey = "test_pubkey_123"
        
        await agent._handle_guidance(mock_event, "!status")
        
        # Verify command handler was called
        mock_cmd_instance.handle_command.assert_called_once()
        # Verify DM was sent
        mock_nostr_instance.send_dm.assert_called_once()


@pytest.mark.asyncio
async def test_guidance_flow_end_to_end(test_env_vars):
    """Test complete guidance flow from DM to post."""
    from pynostr.event import Event
    
    with patch('src.agent.NostrShitposterClient') as mock_nostr, \
         patch('src.agent.OpenRouterProvider') as mock_llm, \
         patch('src.agent.CommandHandler'), \
         patch('src.agent.PostingLoop'), \
         patch('src.agent.RateLimiter') as mock_rate_limiter, \
         patch('src.agent.ContentDeduplicator') as mock_dedup:
        
        # Setup mocks
        mock_nostr_instance = Mock()
        mock_published_event = Mock()
        mock_published_event.id = "published_123"
        mock_nostr_instance.publish_note = AsyncMock(return_value=mock_published_event)
        mock_nostr_instance.send_dm = AsyncMock()
        mock_nostr.return_value = mock_nostr_instance
        
        mock_llm_instance = Mock()
        mock_llm_instance.set_system_prompt = Mock()
        mock_llm_instance.generate_with_guidance = AsyncMock(
            return_value="Post about Bitcoin"
        )
        mock_llm.return_value = mock_llm_instance
        
        # Mock rate limiter
        mock_rate_limiter_instance = Mock()
        mock_rate_limiter_instance.is_allowed = Mock(return_value=True)
        mock_rate_limiter.return_value = mock_rate_limiter_instance
        
        # Mock deduplicator
        mock_dedup_instance = Mock()
        mock_dedup_instance.is_duplicate = Mock(return_value=False)
        mock_dedup.return_value = mock_dedup_instance
        
        agent = ShitposterAgent()
        
        # Simulate receiving guidance DM
        mock_event = Mock(spec=Event)
        mock_event.pubkey = "test_pubkey_123"
        
        await agent._handle_guidance(mock_event, "Make a post about Bitcoin")
        
        # Verify content was generated with guidance
        mock_llm_instance.generate_with_guidance.assert_called_once()
        # Verify post was published
        mock_nostr_instance.publish_note.assert_called_once()
        # Verify confirmation DM was sent
        assert mock_nostr_instance.send_dm.call_count == 1
