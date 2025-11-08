# Hugging Face Spaces App Entry Point
# This file is specifically for Hugging Face Spaces deployment

import os
import sys

# Set environment variables for Hugging Face
os.environ["GRADIO_SERVER_NAME"] = "0.0.0.0"
os.environ["GRADIO_SERVER_PORT"] = "7860"  # Hugging Face default port

# Import and run the main application
from loan_agent_complete import demo

if __name__ == "__main__":
    print("🏦 Starting Tata Capital AI Loan Assistant on Hugging Face Spaces...")
    print("🤗 Hugging Face Spaces deployment detected")
    
    # Launch with Hugging Face specific settings
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        quiet=False
    )