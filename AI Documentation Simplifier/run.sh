#!/bin/bash
# 🚀 Feature Explainer — Quick Start Script
# This script sets up and runs the application

echo "🚀 AI Feature Explainer - Setup & Run"
echo "======================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt --quiet

# Create output directories
mkdir -p output/images output/audio output/explanations

# Check AWS credentials
echo ""
echo "🔑 Checking AWS credentials..."
if aws sts get-caller-identity &>/dev/null; then
    echo "   ✅ AWS credentials are configured"
else
    echo "   ❌ AWS credentials not found!"
    echo "   Run: aws configure"
    echo "   Or set: export AWS_ACCESS_KEY_ID=... and AWS_SECRET_ACCESS_KEY=..."
    exit 1
fi

echo ""
echo "======================================"
echo "Choose how to run:"
echo ""
echo "  1) 🖥️  Streamlit Web UI (recommended)"
echo "  2) 🔌 FastAPI Backend (API mode)"
echo "  3) 📟 CLI mode (terminal)"
echo ""
read -p "Enter choice (1/2/3): " choice

case $choice in
    1)
        echo ""
        echo "🖥️  Starting Streamlit..."
        echo "   Open: http://localhost:8501"
        streamlit run frontend/app.py --server.port 8501
        ;;
    2)
        echo ""
        echo "🔌 Starting FastAPI..."
        echo "   API docs: http://localhost:8000/docs"
        uvicorn backend.app:app --reload --port 8000
        ;;
    3)
        echo ""
        python main.py
        ;;
    *)
        echo "Starting Streamlit (default)..."
        streamlit run frontend/app.py --server.port 8501
        ;;
esac
