#!/bin/bash
# Script to run tests with coverage reporting

# Exit on error
set -e

# Activate virtual environment if not already activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Run tests with coverage
echo "Running tests with coverage..."
python -m pytest tests/ --cov=movie_graph --cov-report=term --cov-report=html

echo "Tests completed!"
echo "See htmlcov/index.html for coverage report." 