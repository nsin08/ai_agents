#!/bin/bash
# Setup script for Interactive Agent Playground with uv

set -e  # Exit on error

echo "🚀 Setting up Interactive Agent Playground environment with uv..."

# Check if uv is installed, install if missing
if ! command -v uv &> /dev/null; then
    echo "⚠ uv is not installed. Installing now..."
    
    # Try pipx first (preferred for isolated tools)
    if command -v pipx &> /dev/null; then
        echo "  Using pipx..."
        pipx install uv
    # Try apt next
    elif command -v apt-get &> /dev/null; then
        echo "  Using apt..."
        sudo apt-get update -qq
        sudo apt-get install -y -qq uv 2>/dev/null || {
            echo "  apt failed, trying pip with --break-system-packages..."
            python3 -m pip install --break-system-packages uv -q
        }
    else
        # Fall back to pip with --break-system-packages for PEP 668 compliance
        echo "  Using pip..."
        python3 -m pip install --break-system-packages uv -q
    fi
    
    # Verify installation
    if ! command -v uv &> /dev/null; then
        echo "❌ Error: Failed to install uv"
        echo "Try manually: python3 -m pip install --break-system-packages uv"
        exit 1
    fi
fi

echo "✓ uv found: $(uv --version)"

# Create Python 3.11 virtual environment
echo ""
echo "📦 Creating virtual environment with Python 3.11..."
uv venv --python 3.11 .venv

# Activate virtual environment
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    echo "✓ Virtual environment activated"
else
    echo "⚠ Could not find activation script"
fi

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
uv pip install -r requirements.txt

# Install development dependencies
echo ""
echo "🔧 Installing development tools..."
uv pip install \
    mypy>=1.0 \
    black>=23.0 \
    ruff>=0.1

# Optional: Install Ollama support
echo ""
echo "Optional: For Ollama integration, run:"
echo "  uv pip install requests>=2.31.0"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Usage:"
echo "  Activate environment:  source .venv/bin/activate  (Linux/macOS)"
echo "                        or .venv\\Scripts\\activate (Windows)"
echo "  Run script:            python interactive_agent.py"
echo "  Deactivate:            deactivate"
echo ""
