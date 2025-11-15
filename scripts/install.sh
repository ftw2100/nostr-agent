#!/bin/bash
# Installation script for Nostr Shitposter Agent

set -e

echo "🚀 Installing Nostr Shitposter Agent..."
echo ""

# Check if pipenv is installed
if ! command -v pipenv &> /dev/null; then
    echo "❌ pipenv is not installed!"
    echo "Installing pipenv..."
    pip install --user pipenv
    export PATH="$HOME/.local/bin:$PATH"
fi

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Install dependencies using pipenv
echo ""
echo "Installing dependencies with pipenv..."
pipenv install --dev

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your API keys!"
    chmod 600 .env
else
    echo "✓ .env file already exists"
fi

# Make scripts executable
chmod +x scripts/*.sh scripts/*.py 2>/dev/null || true

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your API keys"
echo "2. Run: pipenv run python scripts/test_connection.py"
echo "3. Run: pipenv run python -m src.main"
echo ""
echo "💡 Tip: Use 'pipenv shell' to activate the virtual environment"
