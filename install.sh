#!/bin/bash

# Script to install RedEarth-Robotics/rosa fork in editable mode
# This script clones the fork, creates a virtual environment, and installs ROSA

set -e  # Exit on error

# Configuration
REPO_URL="git@github.com:RedEarth-Robotics/rosa.git"
INSTALL_DIR="${INSTALL_DIR:-$HOME/rosa-fork}"
VENV_NAME="venv"

echo "🤖 ROSA Fork Installation Script"
echo "=================================="
echo "Repository: $REPO_URL"
echo "Install directory: $INSTALL_DIR"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Error: git is not installed. Please install git first."
    exit 1
fi

# Check if python3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 is not installed. Please install Python 3.9+ first."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
    echo "❌ Error: Python 3.9+ is required. Current version: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python version: $PYTHON_VERSION"

# Create installation directory if it doesn't exist
if [ -d "$INSTALL_DIR" ]; then
    echo "⚠️  Installation directory already exists: $INSTALL_DIR"
    read -p "Do you want to remove it and reinstall? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Removing existing directory..."
        rm -rf "$INSTALL_DIR"
    else
        echo "❌ Installation cancelled."
        exit 0
    fi
fi

# Clone the repository
echo "📥 Cloning repository from $REPO_URL..."
git clone "$REPO_URL" "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Create virtual environment
echo "🐍 Creating virtual environment..."
python3 -m venv "$VENV_NAME"

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source "$VENV_NAME/bin/activate"

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install ROSA in editable mode with all optional dependencies
echo "📦 Installing ROSA in editable mode with all LLM providers..."
pip install -e ".[all]"

echo ""
echo "✅ Installation completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Activate the virtual environment:"
echo "   source $INSTALL_DIR/$VENV_NAME/bin/activate"
echo ""
echo "2. Verify installation:"
echo "   python -c 'import rosa; print(rosa.__version__)'"
echo ""
echo "3. To deactivate the virtual environment when done:"
echo "   deactivate"
echo ""
echo "🎉 Your ROSA fork is ready to use!"
