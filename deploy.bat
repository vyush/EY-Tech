@echo off
REM Deployment script for Tata Capital AI Loan Assistant (Windows)

echo 🏦 Tata Capital AI Loan Assistant - Deployment Script
echo ==================================================

REM Check Python version
python --version

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt

REM Create environment file if it doesn't exist
if not exist .env (
    echo 🔧 Creating environment file...
    copy .env.example .env
    echo ⚠️  Please edit .env file and add your GEMINI_API_KEY
)

REM Run the application
echo 🚀 Starting Tata Capital AI Loan Assistant...
echo 📱 Access the application at: http://localhost:7861
echo 🔄 Press Ctrl+C to stop the application

python loan_agent_complete.py