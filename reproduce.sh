#!/bin/bash
# Canonical reproduction script for Paper2Repo

set -e

echo "Paper2Repo Reproduction Script"
echo "=============================="
echo

# Check Python version
echo "Checking Python version..."
python3 --version

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install package in editable mode
echo "Installing Paper2Repo..."
pip install --upgrade pip
pip install -e .

# Run tests
echo
echo "Running tests..."
python -m pytest tests/ -v

# Test CLI
echo
echo "Testing CLI..."
python main.py --help
python main.py --version

# Run import check
echo
echo "Testing imports..."
python -c "import paper2repo; print(f'Paper2Repo v{paper2repo.__version__} imported successfully')"

# Compile all files
echo
echo "Compiling Python files..."
python -m compileall paper2repo/

echo
echo "=============================="
echo "✅ All checks passed!"
echo
echo "To use Paper2Repo:"
echo "  source venv/bin/activate"
echo "  python main.py --help"
echo
