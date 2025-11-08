#!/bin/bash
# Deploy to Hugging Face Spaces Script

echo "🤗 Hugging Face Spaces Deployment Script"
echo "========================================"

# Check if huggingface_hub is installed
python -c "import huggingface_hub" 2>/dev/null || {
    echo "📦 Installing Hugging Face Hub..."
    pip install huggingface_hub
}

echo "🔐 Please login to Hugging Face first:"
echo "   Go to: https://huggingface.co/settings/tokens"
echo "   Create a new token with 'write' access"
echo "   Run: huggingface-cli login"
echo ""

read -p "Have you logged in to Hugging Face CLI? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Ready to deploy!"
    echo ""
    echo "📋 Manual steps to complete deployment:"
    echo "1. Go to: https://huggingface.co/spaces"
    echo "2. Click 'Create new Space'"
    echo "3. Name: tata-capital-ai-loan-assistant" 
    echo "4. SDK: Gradio"
    echo "5. Make it Public"
    echo "6. Upload these files:"
    echo "   - app.py (main entry point)"
    echo "   - loan_agent_complete.py (core app)"
    echo "   - requirements.txt"
    echo "   - README.md (rename app.md to README.md)"
    echo ""
    echo "✅ Your Space will be available at:"
    echo "   https://huggingface.co/spaces/YOUR_USERNAME/tata-capital-ai-loan-assistant"
else
    echo "Please login first with: huggingface-cli login"
fi