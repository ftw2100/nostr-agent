"""Tests for posting loop."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from src.posting_loop import PostingLoop


@pytest.fixture
def mock_agent():
    """Create a mock agent."""
    agent = Mock()
    agent.generate_and_post = AsyncMock()
    return agent


@pytest.mark.asyncio
async def test_posting_loop_initialization(mock_agent):
    """Test posting loop initialization."""
    loop = PostingLoop(mock_agent, interval_minutes=30)
    
    assert loop.agent == mock_agent
    assert loop.interval_minutes == 30
    assert loop.interval_seconds == 1800
    assert loop.running == False
    assert loop.last_post_time is None


def test_set_interval(mock_agent):
    """Test setting posting interval."""
    loop = PostingLoop(mock_agent, interval_minutes=60)
    
    loop.set_interval(30)
    
    assert loop.interval_minutes == 30
    assert loop.interval_seconds == 1800


@pytest.mark.asyncio
async def test_posting_loop_run_single_iteration(mock_agent):
    """Test posting loop runs one iteration."""
    loop = PostingLoop(mock_agent, interval_minutes=60)
    
    # Use a very short interval for testing
    loop.interval_seconds = 0.1
    
    # Create a task that will be cancelled after first iteration
    async def run_with_cancel():
        task = asyncio.create_task(loop.run())
        await asyncio.sleep(0.2)  # Wait for first iteration
        loop.stop()
        await asyncio.sleep(0.1)  # Give it time to stop
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    
    await run_with_cancel()
    
    # Verify generate_and_post was called
    assert mock_agent.generate_and_post.called


@pytest.mark.asyncio
async def test_posting_loop_stop(mock_agent):
    """Test stopping the posting loop."""
    loop = PostingLoop(mock_agent, interval_minutes=60)
    loop.running = True
    
    loop.stop()
    
    assert loop.running == False


@pytest.mark.asyncio
async def test_posting_loop_error_handling(mock_agent):
    """Test error handling in posting loop."""
    loop = PostingLoop(mock_agent, interval_minutes=60)
    loop.interval_seconds = 0.1
    
    # Make generate_and_post raise an error
    mock_agent.generate_and_post = AsyncMock(side_effect=Exception("Posting error"))
    
    # Run for a short time
    async def run_with_error():
        task = asyncio.create_task(loop.run())
        await asyncio.sleep(0.2)
        loop.stop()
        await asyncio.sleep(0.1)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    
    await run_with_error()
    
    # Loop should continue running despite error
    assert mock_agent.generate_and_post.called


@pytest.mark.asyncio
async def test_posting_loop_cancelled_error(mock_agent):
    """Test that CancelledError is re-raised."""
    loop = PostingLoop(mock_agent, interval_minutes=60)
    
    # Create a task and cancel it immediately
    task = asyncio.create_task(loop.run())
    task.cancel()
    
    with pytest.raises(asyncio.CancelledError):
        await task
