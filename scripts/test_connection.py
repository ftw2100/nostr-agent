#!/usr/bin/env python3
"""Test script to verify Nostr connectivity and configuration."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config_manager import ConfigManager
from src.nostr_client import NostrShitposterClient
from src.llm_provider import OpenRouterProvider


async def test_nostr_connection():
    """Test Nostr connection and key validation."""
    print("🔍 Testing Nostr Configuration...")
    
    try:
        config = ConfigManager()
        
        # Test key loading
        print("  ✓ Loading private key...")
        nsec = config.get_private_key()
        print(f"  ✓ Private key loaded: {nsec[:10]}...{nsec[-10:]}")
        
        # Test relay loading
        print("  ✓ Loading relays...")
        relays = config.get_relays()
        print(f"  ✓ Loaded {len(relays)} relays:")
        for relay in relays:
            print(f"    - {relay}")
        
        # Test client initialization
        print("  ✓ Initializing Nostr client...")
        client = NostrShitposterClient(relays=relays, private_key=nsec)
        print("  ✓ Nostr client initialized successfully")
        
        # Test publishing a test note
        print("\n📝 Testing note publishing...")
        test_content = "🧪 Test post from Nostr Shitposter Agent - testing connectivity"
        event = await client.publish_note(test_content)
        print(f"  ✓ Successfully published test note: {event.id[:10]}...")
        print(f"  ✓ Event ID: {event.id}")
        print(f"  ✓ Published to {len(relays)} relays")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_llm_connection():
    """Test OpenRouter LLM connection."""
    print("\n🤖 Testing LLM Configuration...")
    
    try:
        config = ConfigManager()
        
        # Test API key
        print("  ✓ Loading API key...")
        api_key = config.get_api_key()
        print("  ✓ API key loaded: [REDACTED]")
        
        # Test model name
        model_name = config.get_model_name()
        print(f"  ✓ Model: {model_name}")
        
        # Test provider initialization
        print("  ✓ Initializing LLM provider...")
        provider = OpenRouterProvider(
            model_name=model_name,
            api_key=api_key,
            base_url=config.get_base_url()
        )
        print("  ✓ LLM provider initialized")
        
        # Test content generation
        print("\n  📝 Testing content generation...")
        provider.set_system_prompt("You are a test agent. Generate a short test message.")
        content = await provider.generate_content()
        print(f"  ✓ Generated content ({len(content)} chars):")
        print(f"    \"{content[:100]}{'...' if len(content) > 100 else ''}\"")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("=" * 60)
    print("Nostr Shitposter Agent - Connection Test")
    print("=" * 60)
    print()
    
    nostr_ok = await test_nostr_connection()
    llm_ok = await test_llm_connection()
    
    print("\n" + "=" * 60)
    if nostr_ok and llm_ok:
        print("✅ All tests passed! Agent is ready to run.")
        return 0
    else:
        print("❌ Some tests failed. Please check your configuration.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
