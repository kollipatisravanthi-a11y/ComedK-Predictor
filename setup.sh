#!/bin/bash
# Quick start script for COMEDK Rank Predictor

echo "=================================="
echo "COMEDK Rank Predictor - Quick Start"
echo "=================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "Error: Python is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Use python3 if available, otherwise use python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "Step 1: Installing dependencies..."
$PYTHON_CMD -m pip install -q -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "✗ Failed to install dependencies"
    exit 1
fi

echo ""
echo "Step 2: Generating training data..."
$PYTHON_CMD data_generator.py
if [ $? -eq 0 ]; then
    echo "✓ Training data generated successfully"
else
    echo "✗ Failed to generate training data"
    exit 1
fi

echo ""
echo "Step 3: Training the AI model..."
$PYTHON_CMD train_model.py
if [ $? -eq 0 ]; then
    echo "✓ Model trained successfully"
else
    echo "✗ Failed to train model"
    exit 1
fi

echo ""
echo "=================================="
echo "Setup Complete! 🎉"
echo "=================================="
echo ""
echo "To start the web application, run:"
echo "  $PYTHON_CMD app.py"
echo ""
echo "Then open your browser and visit:"
echo "  http://localhost:5000"
echo ""
