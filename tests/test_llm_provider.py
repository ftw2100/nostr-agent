"""Tests for LLM provider."""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.language_models.chat_models import BaseChatModel

from src.llm_provider import OpenRouterProvider


@pytest.fixture
def mock_llm():
    """Create a mock LLM."""
    llm = Mock(spec=BaseChatModel)
    llm.ainvoke = AsyncMock()
    return llm


@pytest.fixture
def provider_config():
    """Provider configuration."""
    return {
        "model_name": "openai/gpt-4o-mini",
        "api_key": "test_api_key",
        "base_url": "https://openrouter.ai/api/v1"
    }


@pytest.mark.asyncio
async def test_llm_provider_initialization(provider_config):
    """Test LLM provider initialization."""
    with patch('src.llm_provider.ChatOpenAI') as mock_chat:
        provider = OpenRouterProvider(**provider_config)
        
        assert provider.system_prompt == ""
        assert provider.model_name == provider_config["model_name"]
        mock_chat.assert_called_once()


def test_set_system_prompt(provider_config):
    """Test setting system prompt."""
    with patch('src.llm_provider.ChatOpenAI'):
        provider = OpenRouterProvider(**provider_config)
        
        prompt = "You are a test agent."
        provider.set_system_prompt(prompt)
        
        assert provider.system_prompt == prompt


@pytest.mark.asyncio
async def test_generate_content_success(provider_config):
    """Test successful content generation."""
    mock_response = Mock()
    mock_response.content = "Generated test content"
    
    with patch('src.llm_provider.ChatOpenAI') as mock_chat:
        mock_llm_instance = Mock()
        mock_llm_instance.ainvoke = AsyncMock(return_value=mock_response)
        mock_chat.return_value = mock_llm_instance
        
        provider = OpenRouterProvider(**provider_config)
        provider.set_system_prompt("Test prompt")
        provider.llm = mock_llm_instance
        
        result = await provider.generate_content()
        
        assert result == "Generated test content"
        assert mock_llm_instance.ainvoke.called


@pytest.mark.asyncio
async def test_generate_content_with_context(provider_config):
    """Test content generation with context."""
    mock_response = Mock()
    mock_response.content = "Generated content with context"
    
    with patch('src.llm_provider.ChatOpenAI') as mock_chat:
        mock_llm_instance = Mock()
        mock_llm_instance.ainvoke = AsyncMock(return_value=mock_response)
        mock_chat.return_value = mock_llm_instance
        
        provider = OpenRouterProvider(**provider_config)
        provider.set_system_prompt("Test prompt")
        provider.llm = mock_llm_instance
        
        context = {"topic": "Bitcoin", "mood": "bullish"}
        result = await provider.generate_content(context=context)
        
        assert result == "Generated content with context"
        # Verify context was included in messages
        call_args = mock_llm_instance.ainvoke.call_args[0][0]
        assert len(call_args) >= 2  # System message + context + generation prompt


@pytest.mark.asyncio
async def test_generate_content_empty_prompt(provider_config):
    """Test that empty system prompt raises error."""
    with patch('src.llm_provider.ChatOpenAI'):
        provider = OpenRouterProvider(**provider_config)
        # Don't set system prompt (stays empty)
        
        with pytest.raises(ValueError, match="System prompt is not set"):
            await provider.generate_content()


@pytest.mark.asyncio
async def test_generate_content_content_too_long(provider_config):
    """Test that content longer than 2000 chars is truncated."""
    mock_response = Mock()
    mock_response.content = "x" * 2500  # Very long content
    
    with patch('src.llm_provider.ChatOpenAI') as mock_chat:
        mock_llm_instance = Mock()
        mock_llm_instance.ainvoke = AsyncMock(return_value=mock_response)
        mock_chat.return_value = mock_llm_instance
        
        provider = OpenRouterProvider(**provider_config)
        provider.set_system_prompt("Test prompt")
        provider.llm = mock_llm_instance
        
        result = await provider.generate_content()
        
        assert len(result) <= 2000
        assert result.endswith("...")


@pytest.mark.asyncio
async def test_generate_with_guidance_success(provider_config):
    """Test successful content generation with guidance."""
    mock_response = Mock()
    mock_response.content = "Generated content with guidance"
    
    with patch('src.llm_provider.ChatOpenAI') as mock_chat:
        mock_llm_instance = Mock()
        mock_llm_instance.ainvoke = AsyncMock(return_value=mock_response)
        mock_chat.return_value = mock_llm_instance
        
        provider = OpenRouterProvider(**provider_config)
        provider.set_system_prompt("Test prompt")
        provider.llm = mock_llm_instance
        
        guidance = "Make a post about Bitcoin"
        result = await provider.generate_with_guidance(guidance)
        
        assert result == "Generated content with guidance"
        # Verify guidance was included
        call_args = mock_llm_instance.ainvoke.call_args[0][0]
        assert any("guidance" in str(msg.content).lower() for msg in call_args)


@pytest.mark.asyncio
async def test_generate_with_guidance_empty_prompt(provider_config):
    """Test that empty system prompt raises error."""
    with patch('src.llm_provider.ChatOpenAI'):
        provider = OpenRouterProvider(**provider_config)
        
        with pytest.raises(ValueError, match="System prompt is not set"):
            await provider.generate_with_guidance("test guidance")


@pytest.mark.asyncio
async def test_generate_with_guidance_empty_guidance(provider_config):
    """Test that empty guidance raises error."""
    with patch('src.llm_provider.ChatOpenAI'):
        provider = OpenRouterProvider(**provider_config)
        provider.set_system_prompt("Test prompt")
        
        with pytest.raises(ValueError, match="Guidance cannot be empty"):
            await provider.generate_with_guidance("")
        
        with pytest.raises(ValueError, match="Guidance cannot be empty"):
            await provider.generate_with_guidance("   ")


@pytest.mark.asyncio
async def test_generate_content_llm_error(provider_config):
    """Test error handling when LLM call fails."""
    with patch('src.llm_provider.ChatOpenAI') as mock_chat:
        mock_llm_instance = Mock()
        mock_llm_instance.ainvoke = AsyncMock(side_effect=Exception("LLM API error"))
        mock_chat.return_value = mock_llm_instance
        
        provider = OpenRouterProvider(**provider_config)
        provider.set_system_prompt("Test prompt")
        provider.llm = mock_llm_instance
        
        with pytest.raises(Exception, match="Content generation failed"):
            await provider.generate_content()
