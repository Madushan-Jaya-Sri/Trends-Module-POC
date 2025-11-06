#!/bin/bash

# Social Media Trends API - Start Script
# This script starts the FastAPI backend server

echo "=€ Starting Social Media Trends API..."
echo ""
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "L Virtual environment not found!"
    echo "Please create one with: python3 -m venv venv"
    echo "Then install requirements: pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "=æ Activating virtual environment..."
source venv/bin/activate

# Check if required packages are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "L FastAPI not found!"
    echo "Installing requirements..."
    pip install -r requirements.txt
fi

echo ""
echo " Starting FastAPI server..."
echo ""
echo ""
echo "=Í API Server: http://localhost:8000"
echo "=Ú API Docs: http://localhost:8000/docs"
echo "<¨ Frontend: Open frontend/index.html in your browser"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
cd /Users/jayasri/Documents/Trends-Module-POC
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
