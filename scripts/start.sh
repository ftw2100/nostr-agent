#!/bin/bash
# Start script for Nostr Shitposter Agent

set -e

# Check if pipenv is installed
if ! command -v pipenv &> /dev/null; then
    echo "❌ pipenv is not installed!"
    echo "Please run: pip install --user pipenv"
    exit 1
fi

# Check if Pipfile exists
if [ ! -f "Pipfile" ]; then
    echo "❌ Error: Pipfile not found!"
    echo "Please run ./scripts/install.sh first."
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "Please copy .env.example to .env and configure it."
    exit 1
fi

# Start the agent using pipenv
echo "🚀 Starting Nostr Shitposter Agent..."
pipenv run python -m src.main "$@"
