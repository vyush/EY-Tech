#!/bin/bash
# Deployment script for Tata Capital AI Loan Assistant

echo "🏦 Tata Capital AI Loan Assistant - Deployment Script"
echo "=================================================="

# Check Python version
python --version

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "🔧 Creating environment file..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your GEMINI_API_KEY"
fi

# Run the application
echo "🚀 Starting Tata Capital AI Loan Assistant..."
echo "📱 Access the application at: http://localhost:7861"
echo "🔄 Press Ctrl+C to stop the application"

python loan_agent_complete.py