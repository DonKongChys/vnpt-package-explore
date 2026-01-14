#!/bin/bash

# Script to run tests with py312 environment

echo "=================================================="
echo "Package Search & Report Tool - Test Runner"
echo "=================================================="
echo ""

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "❌ Conda not found. Please install Miniconda/Anaconda first."
    exit 1
fi

# Activate py312 environment
echo "🔄 Activating py312 environment..."
eval "$(conda shell.bash hook)"
conda activate py312

if [ $? -ne 0 ]; then
    echo "❌ Failed to activate py312 environment"
    exit 1
fi

echo "✅ Environment activated: $(which python)"
echo "   Python version: $(python --version)"
echo ""

# Check if dependencies are installed
echo "🔍 Checking dependencies..."
python -c "import pandas, openpyxl, rapidfuzz, streamlit" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "⚠️ Some dependencies are missing. Installing..."
    pip install -r requirements.txt
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
    echo "✅ Dependencies installed"
else
    echo "✅ All dependencies are installed"
fi
echo ""

# Run tests
echo "🧪 Running module tests..."
python test_modules.py

if [ $? -eq 0 ]; then
    echo ""
    echo "=================================================="
    echo "✅ All tests passed!"
    echo "=================================================="
    echo ""
    echo "To run the Streamlit app:"
    echo "  conda activate py312"
    echo "  cd $(pwd)"
    echo "  streamlit run app.py"
    echo ""
else
    echo ""
    echo "❌ Tests failed. Please check the errors above."
    exit 1
fi
