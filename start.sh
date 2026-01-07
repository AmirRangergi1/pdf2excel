#!/bin/bash

echo "🚀 PDF to Excel Converter - Quick Start"
echo "========================================"
echo ""
echo "Setting up Backend..."
echo ""

cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing backend dependencies..."
pip install -r requirements.txt

# Start backend in background
echo "Starting FastAPI backend on http://localhost:8000..."
python main.py &
BACKEND_PID=$!

sleep 2

echo ""
echo "Setting up Frontend..."
echo ""

cd ../frontend

# Install dependencies
echo "Installing frontend dependencies..."
npm install

# Start frontend
echo "Starting Vue.js frontend on http://localhost:5173..."
echo ""
echo "✅ Application is ready! Open http://localhost:5173 in your browser"
echo ""
echo "To stop the application, press Ctrl+C"
echo ""

npm run dev

# Cleanup
kill $BACKEND_PID
