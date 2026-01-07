#!/bin/bash

echo "🚀 PDF to Excel Converter - Starting Application"
echo "=================================================="
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Build Frontend
echo "📦 Building Frontend..."
echo ""

cd frontend

# Create virtual environment if it doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Build the frontend
echo "Building Vue.js application..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Frontend build failed!"
    exit 1
fi

echo "✅ Frontend built successfully!"
echo ""

# Setup Backend
echo "🔧 Setting up Backend..."
echo ""

cd ../backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing backend dependencies..."
pip install -r requirements.txt --quiet

if [ $? -ne 0 ]; then
    echo "❌ Backend setup failed!"
    exit 1
fi

echo "✅ Backend setup complete!"
echo ""

# Start backend
echo "🌐 Starting FastAPI Backend..."
echo "    Backend: http://localhost:8000"
echo ""
echo "=========================================="
echo "Application is ready!"
echo "=========================================="
echo ""
echo "Open your browser to: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

python main.py
