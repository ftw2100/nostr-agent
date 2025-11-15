"""LLM provider using OpenRouter API via LangChain."""

import os
from typing import Optional, Dict
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from agentstr.logger import get_logger

from .constants import (
    MAX_LLM_TOKENS,
    LLM_TIMEOUT_SECONDS,
    LLM_TEMPERATURE,
    MAX_NOTE_LENGTH
)
from .circuit_breaker import CircuitBreaker
from .constants import CIRCUIT_BREAKER_FAILURE_THRESHOLD, CIRCUIT_BREAKER_TIMEOUT

logger = get_logger(__name__)


class OpenRouterProvider:
    """LLM provider using OpenRouter API."""
    
    def __init__(self, model_name: str, api_key: str, base_url: str):
        """Initialize OpenRouter provider.
        
        Args:
            model_name: Model identifier (e.g., "openai/gpt-4o-mini").
            api_key: OpenRouter API key.
            base_url: OpenRouter API base URL.
        """
        self.llm = ChatOpenAI(
            model_name=model_name,
            api_key=api_key,
            base_url=base_url,
            temperature=LLM_TEMPERATURE,
            max_tokens=MAX_LLM_TOKENS,
            timeout=LLM_TIMEOUT_SECONDS,
        )
        self.system_prompt = ""
        self.model_name = model_name
        # Initialize circuit breaker for LLM calls
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=CIRCUIT_BREAKER_FAILURE_THRESHOLD,
            timeout=CIRCUIT_BREAKER_TIMEOUT
        )
        logger.info(f"Initialized OpenRouter provider with model: {model_name}")
    
    def set_system_prompt(self, prompt: str):
        """Update the system prompt.
        
        Args:
            prompt: New system prompt.
        """
        self.system_prompt = prompt
        logger.info("System prompt updated")
    
    def _validate_content(self, content: str) -> str:
        """Validate and clean generated content.
        
        Args:
            content: Raw content from LLM.
            
        Returns:
            Validated and cleaned content.
        """
        content = content.strip()
        
        # Remove empty content
        if not content:
            raise ValueError("Generated content is empty")
        
        # Limit length (Nostr practical limit)
        if len(content) > MAX_NOTE_LENGTH:
            logger.warning(f"Content too long ({len(content)} chars), truncating to {MAX_NOTE_LENGTH}")
            content = content[:MAX_NOTE_LENGTH - 3] + "..."
        
        return content
    
    async def generate_content(self, context: Optional[Dict] = None) -> str:
        """Generate shitpost content.
        
        Args:
            context: Optional context dictionary for generation.
            
        Returns:
            Generated content string.
            
        Raises:
            Exception: If generation fails.
        """
        if not self.system_prompt or not self.system_prompt.strip():
            raise ValueError("System prompt is not set. Please configure the agent personality.")
        
        try:
            messages = [SystemMessage(content=self.system_prompt)]
            
            if context:
                context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
                messages.append(HumanMessage(content=f"Context: {context_str}"))
            
            messages.append(
                HumanMessage(
                    content="Generate a witty Nostr shitpost. "
                           "Keep it concise (under 500 characters), engaging, and authentic. "
                           "No hashtags unless natural."
                )
            )
            
            logger.info("Generating content with LLM...")
            # Use circuit breaker to protect against API failures
            response = await self.circuit_breaker.call_async(
                self.llm.ainvoke,
                messages
            )
            content = self._validate_content(response.content)
            logger.info(f"Generated content ({len(content)} chars)")
            return content
            
        except Exception as e:
            logger.error(f"Failed to generate content: {e}")
            raise Exception(f"Content generation failed: {e}")
    
    async def generate_with_guidance(self, guidance: str) -> str:
        """Generate content with specific guidance.
        
        Args:
            guidance: User-provided guidance for the post.
            
        Returns:
            Generated content following the guidance.
            
        Raises:
            Exception: If generation fails.
        """
        if not self.system_prompt or not self.system_prompt.strip():
            raise ValueError("System prompt is not set. Please configure the agent personality.")
        
        if not guidance or not guidance.strip():
            raise ValueError("Guidance cannot be empty")
        
        try:
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(
                    content=f"User guidance: {guidance}\n\n"
                           "Generate a Nostr post following this guidance. "
                           "Keep it concise (under 500 characters), engaging, and authentic."
                )
            ]
            
            logger.info(f"Generating content with guidance: {guidance[:50]}...")
            # Use circuit breaker to protect against API failures
            response = await self.circuit_breaker.call_async(
                self.llm.ainvoke,
                messages
            )
            content = self._validate_content(response.content)
            logger.info(f"Generated content with guidance ({len(content)} chars)")
            return content
            
        except Exception as e:
            logger.error(f"Failed to generate content with guidance: {e}")
            raise Exception(f"Content generation with guidance failed: {e}")
