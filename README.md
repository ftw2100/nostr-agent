# Nostr Shitposter Agent

A professional, autonomous Nostr agent powered by AI that automatically generates and posts engaging content to the Nostr network. Control and guide the agent through direct messages, or let it run autonomously with configurable posting intervals.

## Features

- 🤖 **Autonomous Posting**: Automatically generates and posts content at configurable intervals
- 💬 **DM Guidance**: Receive guidance via direct messages to influence the next post
- 🎛️ **Command System**: Control the agent with simple commands (`!status`, `!post-now`, etc.)
- 🔧 **Easy Configuration**: YAML-based configuration with modular prompts
- 🔒 **Secure**: Proper secret management with environment variables
- 🚀 **Production Ready**: Error handling, retry logic, and comprehensive logging

## Prerequisites

- Python 3.10 or higher
- A Nostr private key (nsec format) - get one from any Nostr client
- An [OpenRouter](https://openrouter.ai/) API key for LLM access

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/ftw2100/nostr-agent.git
cd nostr-agent

# Run installation script (recommended)
./scripts/install.sh

# Or manually with pipenv:
pip install --user pipenv
pipenv install --dev

# Or with pip:
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your keys:
# - NOSTR_NSEC: Your Nostr private key (nsec format)
# - OPENROUTER_API_KEY: Your OpenRouter API key
# - LLM_MODEL_NAME: Model to use (e.g., "openai/gpt-4o-mini")
```

### 3. Test Connection

```bash
# Test Nostr and LLM connectivity
pipenv run python scripts/test_connection.py

# Or activate the shell first:
pipenv shell
python scripts/test_connection.py
```

### 4. Run

```bash
# Start the agent (recommended)
./scripts/start.sh

# Or directly with pipenv:
pipenv run python -m src.main

# Or activate the shell first:
pipenv shell
python -m src.main
```

## Configuration

### Environment Variables (.env)

```bash
# Nostr Configuration
NOSTR_NSEC=nsec1...                    # Your Nostr private key
NOSTR_RELAYS=wss://relay.damus.io,...  # Comma-separated relay URLs

# OpenRouter Configuration
OPENROUTER_API_KEY=your_key_here       # Your OpenRouter API key
LLM_MODEL_NAME=openai/gpt-4o-mini     # Model identifier
LLM_BASE_URL=https://openrouter.ai/api/v1

# Agent Configuration
POSTING_INTERVAL_MINUTES=60            # Posting interval

# Security Configuration (Optional but Recommended)
AUTHORIZED_PUBKEYS=pubkey1,pubkey2     # Comma-separated list of authorized public keys for commands
                                        # If not set, all users can use commands (backward compatible)
```

### Agent Configuration (config/agent.yaml)

```yaml
agent:
  name: "Shitposter Agent"
  personality: |
    Your agent personality and behavior instructions...

posting:
  interval_minutes: 60
  min_interval: 30
  max_interval: 120

guidance:
  enabled: true
  commands_enabled: true
```

### System Prompt (config/prompts/system_prompt.txt)

Edit this file to customize the agent's personality and posting style.

## Usage

### Starting the Agent

```bash
# Start with default config
pipenv run python -m src.main

# Start with custom config
pipenv run python -m src.main config/custom.yaml

# Or use the start script
./scripts/start.sh config/custom.yaml
```

### Direct Message Commands

Send direct messages to the agent's public key to control it:

- `!status` - Show agent status
- `!set-prompt <text>` - Update system prompt
- `!post-now` - Force immediate post
- `!set-interval <minutes>` - Change posting interval
- `!help` - Show available commands

### Guidance Messages

Send regular messages (without `!`) to provide guidance for the next post. The agent will generate content following your guidance.

Example:
```
"Make a post about Bitcoin's recent price action"
```

## Architecture

```
┌─────────────────────────────────────────┐
│         Shitposter Agent               │
├─────────────────────────────────────────┤
│  Config Manager → Agent Core → Nostr   │
│       ↓              ↓          ↓       │
│   LLM Provider    Commands   Relays     │
└─────────────────────────────────────────┘
```

### Components

- **ConfigManager**: Loads and manages configuration
- **NostrShitposterClient**: Handles Nostr protocol operations
- **OpenRouterProvider**: LLM integration via OpenRouter
- **CommandHandler**: Processes DM commands
- **PostingLoop**: Manages autonomous posting schedule
- **ShitposterAgent**: Main orchestrator

## Development

### Project Structure

```
nostr-agent/
├── src/                    # Source code
│   ├── agent.py           # Main agent class
│   ├── nostr_client.py    # Nostr wrapper
│   ├── llm_provider.py    # LLM integration
│   ├── command_handler.py # Command system
│   ├── posting_loop.py    # Posting scheduler
│   └── config_manager.py  # Configuration
├── config/                 # Configuration files
│   ├── agent.yaml         # Main config
│   └── prompts/           # Prompt templates
├── scripts/                # Utility scripts
│   ├── install.sh         # Installation
│   ├── start.sh           # Start script
│   └── test_connection.py # Connection test
├── tests/                  # Tests
└── logs/                   # Log files
```

### Running Tests

```bash
# Run all tests
pipenv run pytest tests/

# Run specific test
pipenv run pytest tests/test_nostr.py

# Or activate shell first:
pipenv shell
pytest tests/
```

### Testing Connectivity

```bash
# Test Nostr and LLM connections
pipenv run python scripts/test_connection.py
```

## Security

- **Secret Management**: All secrets stored in `.env` (never committed)
- **Key Validation**: Validates nsec format on startup
- **Content Validation**: Validates content length and format
- **Error Handling**: Comprehensive error handling and logging
- **Command Authentication**: Optional authorized users list for commands (set `AUTHORIZED_PUBKEYS` in `.env`)
- **Rate Limiting**: Built-in rate limiting for commands (10/hour) and guidance (5/hour) per user
- **Input Sanitization**: All user inputs are sanitized to prevent injection attacks
- **Content Deduplication**: Prevents posting duplicate or very similar content
- **Minimum Posting Interval**: Enforces minimum 30-second interval to prevent spam

## Troubleshooting

### Connection Issues

```bash
# Test Nostr connectivity
pipenv run python scripts/test_connection.py

# Check relay URLs in .env
# Verify NOSTR_NSEC is correct
```

### LLM Issues

```bash
# Verify OpenRouter API key
# Check model name is correct
# Test with: pipenv run python scripts/test_connection.py
```

### Posting Failures

- Check relay connectivity
- Verify content length (max ~2000 chars)
- Check logs in `logs/` directory

## Production Deployment

### Using systemd

```ini
# /etc/systemd/system/nostr-shitposter.service
[Unit]
Description=Nostr Shitposter Agent
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/nostr-agent
Environment="PATH=/home/youruser/.local/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/bin/pipenv run python -m src.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable nostr-shitposter
sudo systemctl start nostr-shitposter
sudo systemctl status nostr-shitposter
```

### Using Supervisor

```ini
# supervisor.conf
[program:nostr-shitposter]
command=/usr/bin/pipenv run python -m src.main
directory=/path/to/nostr-agent
autostart=true
autorestart=true
stderr_logfile=/var/log/nostr-shitposter/error.log
stdout_logfile=/var/log/nostr-shitposter/output.log
environment=PATH="/home/youruser/.local/bin:/usr/local/bin:/usr/bin:/bin"
```

## License

MIT License

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

Quick start:
1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

For security issues, please see [SECURITY.md](SECURITY.md).

## Support

For issues and questions:
1. Check the [troubleshooting section](#troubleshooting) above
2. Review logs in `logs/` directory
3. Check the [CHANGELOG.md](CHANGELOG.md) for recent changes
4. Open an issue on GitHub

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [agentstr-sdk](https://github.com/agentstr/agentstr-sdk) and [pynostr](https://github.com/jeffthibault/python-nostr)
- LLM integration via [OpenRouter](https://openrouter.ai/)
- Powered by [LangChain](https://www.langchain.com/)

---

**Note**: This is an open source project. Use responsibly and ensure you comply with Nostr relay policies and terms of service.
