#!/bin/bash
# Script to set up a new virtual environment for the project

# Exit on error
set -e

echo "Setting up virtual environment..."

# Remove existing venv if it exists
if [ -d ".venv" ]; then
    echo "Removing existing virtual environment..."
    rm -rf .venv
fi

# Create new virtual environment
echo "Creating new virtual environment..."
python3 -m venv .venv

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Optional: Install development dependencies
echo "Installing development dependencies..."
pip install pytest pytest-cov black flake8 mypy

echo "Virtual environment setup complete!"
echo "To activate the virtual environment, run:"
echo "source .venv/bin/activate" 