"""Tests for Nostr client wrapper."""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from pynostr.event import Event, EventKind
from pynostr.key import PrivateKey

from src.nostr_client import NostrShitposterClient


@pytest.fixture
def mock_base_client():
    """Create a mock base NostrClient."""
    client = Mock()
    client.relay_manager = Mock()
    client.relay_manager.send_event = AsyncMock()
    client.send_direct_message = AsyncMock()
    client.update_metadata = AsyncMock()
    client.direct_message_listener = AsyncMock()
    return client


@pytest.fixture
def test_nsec():
    """Test Nostr private key."""
    return "nsec14htkwc05374nh2ke77g93ljpz6xtf88zh3nzgh0upjgxmglxeemszdnxvq"


@pytest.fixture
def test_relays():
    """Test relay URLs."""
    return ["wss://relay.damus.io", "wss://nostr-pub.wellorder.net"]


@pytest.mark.asyncio
async def test_nostr_client_initialization(mock_base_client, test_relays, test_nsec):
    """Test Nostr client initialization."""
    with patch('src.nostr_client.BaseNostrClient', return_value=mock_base_client):
        client = NostrShitposterClient(relays=test_relays, private_key=test_nsec)
        assert client.relays == test_relays
        assert client.private_key == test_nsec
        assert client.client == mock_base_client


@pytest.mark.asyncio
async def test_publish_note_success(mock_base_client, test_relays, test_nsec):
    """Test successful note publishing."""
    # Create a mock event
    mock_event = Mock(spec=Event)
    mock_event.id = "test_event_id_12345"
    mock_base_client.relay_manager.send_event = AsyncMock(return_value=mock_event)
    
    with patch('src.nostr_client.BaseNostrClient', return_value=mock_base_client):
        client = NostrShitposterClient(relays=test_relays, private_key=test_nsec)
        
        content = "Test post content"
        result = await client.publish_note(content)
        
        assert result == mock_event
        mock_base_client.relay_manager.send_event.assert_called_once()


@pytest.mark.asyncio
async def test_publish_note_empty_content(mock_base_client, test_relays, test_nsec):
    """Test publishing empty content raises error."""
    with patch('src.nostr_client.BaseNostrClient', return_value=mock_base_client):
        client = NostrShitposterClient(relays=test_relays, private_key=test_nsec)
        
        with pytest.raises(ValueError, match="Content cannot be empty"):
            await client.publish_note("")
        
        with pytest.raises(ValueError, match="Content cannot be empty"):
            await client.publish_note("   ")


@pytest.mark.asyncio
async def test_publish_note_content_too_long(mock_base_client, test_relays, test_nsec):
    """Test that content longer than 2000 chars is truncated."""
    mock_event = Mock(spec=Event)
    mock_event.id = "test_event_id"
    mock_base_client.relay_manager.send_event = AsyncMock(return_value=mock_event)
    
    with patch('src.nostr_client.BaseNostrClient', return_value=mock_base_client):
        client = NostrShitposterClient(relays=test_relays, private_key=test_nsec)
        
        # Create content longer than 2000 chars
        long_content = "x" * 2500
        result = await client.publish_note(long_content)
        
        # Verify event was called with truncated content
        call_args = mock_base_client.relay_manager.send_event.call_args[0][0]
        assert len(call_args.content) <= 2000
        assert call_args.content.endswith("...")


@pytest.mark.asyncio
async def test_publish_note_retry_on_failure(mock_base_client, test_relays, test_nsec):
    """Test retry logic on publishing failure."""
    mock_event = Mock(spec=Event)
    mock_event.id = "test_event_id"
    
    # First call fails, second succeeds
    mock_base_client.relay_manager.send_event = AsyncMock(
        side_effect=[Exception("Network error"), mock_event]
    )
    
    with patch('src.nostr_client.BaseNostrClient', return_value=mock_base_client):
        with patch('asyncio.sleep', new_callable=AsyncMock):  # Speed up test
            client = NostrShitposterClient(relays=test_relays, private_key=test_nsec)
            
            content = "Test post"
            result = await client.publish_note(content, max_retries=3)
            
            assert result == mock_event
            assert mock_base_client.relay_manager.send_event.call_count == 2


@pytest.mark.asyncio
async def test_publish_note_all_retries_fail(mock_base_client, test_relays, test_nsec):
    """Test that exception is raised when all retries fail."""
    mock_base_client.relay_manager.send_event = AsyncMock(
        side_effect=Exception("Persistent error")
    )
    
    with patch('src.nostr_client.BaseNostrClient', return_value=mock_base_client):
        with patch('asyncio.sleep', new_callable=AsyncMock):
            client = NostrShitposterClient(relays=test_relays, private_key=test_nsec)
            
            with pytest.raises(Exception, match="Failed to publish note after"):
                await client.publish_note("Test post", max_retries=2)


@pytest.mark.asyncio
async def test_send_dm_success(mock_base_client, test_relays, test_nsec):
    """Test successful DM sending."""
    mock_event = Mock(spec=Event)
    mock_event.id = "dm_event_id"
    mock_base_client.send_direct_message = AsyncMock(return_value=mock_event)
    
    with patch('src.nostr_client.BaseNostrClient', return_value=mock_base_client):
        client = NostrShitposterClient(relays=test_relays, private_key=test_nsec)
        
        result = await client.send_dm("recipient_pubkey", "Test message")
        
        assert result == mock_event
        mock_base_client.send_direct_message.assert_called_once_with(
            "recipient_pubkey", "Test message"
        )


@pytest.mark.asyncio
async def test_listen_for_guidance(mock_base_client, test_relays, test_nsec):
    """Test guidance listener setup."""
    callback = Mock()
    
    with patch('src.nostr_client.BaseNostrClient', return_value=mock_base_client):
        client = NostrShitposterClient(relays=test_relays, private_key=test_nsec)
        
        await client.listen_for_guidance(callback)
        
        mock_base_client.direct_message_listener.assert_called_once_with(
            callback=callback,
            recipient_pubkey=None
        )


@pytest.mark.asyncio
async def test_update_metadata(mock_base_client, test_relays, test_nsec):
    """Test metadata update."""
    mock_base_client.update_metadata = AsyncMock()
    
    with patch('src.nostr_client.BaseNostrClient', return_value=mock_base_client):
        client = NostrShitposterClient(relays=test_relays, private_key=test_nsec)
        
        await client.update_metadata(
            name="Test Agent",
            about="Test description",
            picture="https://example.com/pic.jpg"
        )
        
        mock_base_client.update_metadata.assert_called_once_with(
            name="Test Agent",
            about="Test description",
            picture="https://example.com/pic.jpg"
        )
