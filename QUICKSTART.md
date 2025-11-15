# Quick Start Guide

> **Note**: For detailed documentation, see [README.md](README.md). This guide provides a condensed setup process.

## Prerequisites

- Python 3.10 or higher
- Nostr private key (nsec format) - get one from any Nostr client
- [OpenRouter](https://openrouter.ai/) API key

## Step-by-Step Setup

### 1. Install Dependencies

```bash
cd nostr-agent
./scripts/install.sh
```

Or manually:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit .env with your favorite editor
nano .env  # or vim, code, etc.
```

Required variables:
- `NOSTR_NSEC`: Your Nostr private key (nsec format)
- `OPENROUTER_API_KEY`: Your OpenRouter API key
- `LLM_MODEL_NAME`: Model to use (e.g., "openai/gpt-4o-mini")

Optional variables:
- `NOSTR_RELAYS`: Comma-separated relay URLs (defaults provided)
- `POSTING_INTERVAL_MINUTES`: Posting interval (default: 60)

### 3. Test Connection

```bash
python scripts/test_connection.py
```

This will:
- ✅ Validate your Nostr key
- ✅ Test relay connectivity
- ✅ Publish a test note
- ✅ Test LLM connectivity
- ✅ Generate test content

### 4. Customize Agent Personality

Edit `config/prompts/system_prompt.txt` or `config/agent.yaml` to customize:
- Agent personality
- Posting style
- Content guidelines

### 5. Start the Agent

```bash
./scripts/start.sh
```

Or:
```bash
python -m src.main
```

The agent will:
- Connect to Nostr relays
- Start posting autonomously
- Listen for DM guidance
- Respond to commands

## Using the Agent

### Direct Message Commands

Send DMs to the agent's public key:

- `!status` - Check agent status
- `!post-now` - Force immediate post
- `!set-prompt <text>` - Update system prompt
- `!set-interval <minutes>` - Change posting interval
- `!help` - Show help

### Providing Guidance

Send regular messages (without `!`) to guide the next post:

```
"Make a post about Bitcoin's recent developments"
```

The agent will generate and post content following your guidance.

## Troubleshooting

### Connection Issues

```bash
# Test connectivity
python scripts/test_connection.py

# Check .env file
cat .env

# Verify key format
# nsec keys start with "nsec1"
```

### LLM Issues

- Verify OpenRouter API key is correct
- Check model name is valid
- Ensure you have credits on OpenRouter

### Posting Failures

- Check relay URLs are correct
- Verify content length (max ~2000 chars)
- Check logs in `logs/` directory

## Production Deployment

### Using systemd

Create `/etc/systemd/system/nostr-shitposter.service`:

```ini
[Unit]
Description=Nostr Shitposter Agent
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/nostr-agent
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python -m src.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable nostr-shitposter
sudo systemctl start nostr-shitposter
sudo systemctl status nostr-shitposter
```

## Next Steps

1. ✅ Test connection
2. ✅ Customize personality
3. ✅ Start agent
4. ✅ Monitor posts
5. ✅ Provide guidance via DMs

Enjoy your autonomous Nostr shitposter! 🚀
