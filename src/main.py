"""Main entry point for the Nostr Shitposter Agent."""

import asyncio
import sys
from pathlib import Path
from agentstr.logger import get_logger

from .agent import ShitposterAgent

logger = get_logger(__name__)


async def main():
    """Main entry point."""
    try:
        # Determine config path
        config_path = "config/agent.yaml"
        if len(sys.argv) > 1:
            config_path = sys.argv[1]
        
        # Check if config exists
        if not Path(config_path).exists():
            logger.warning(f"Config file not found: {config_path}, using defaults")
        
        # Create and start agent
        agent = ShitposterAgent(config_path=config_path)
        await agent.start()
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
