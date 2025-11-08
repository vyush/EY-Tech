# app.py - Hugging Face Spaces Deployment
# Enhanced Agentic AI Loan Assistant for NBFC
# Implements Master Agent + 4 Worker Agents with full workflow

import gradio as gr
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
import pandas as pd
import random
import os
import json
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables (for local development)
load_dotenv()

# Get API key from environment variables (Hugging Face Spaces compatible)
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

print("=" * 60)
print("🤖 TATA CAPITAL AI LOAN ASSISTANT - HUGGING FACE SPACES")
print("=" * 60)
if api_key:
    genai.configure(api_key=api_key)
    print("✅ GOOGLE GEMINI AI: Successfully configured and ready!")
    print(f"🔑 API Key: {api_key[:15]}...{api_key[-5:] if len(api_key) > 20 else 'CONFIGURED'}")
    print("🚀 AI FEATURES: Enhanced greetings, smart responses, contextual conversations")
else:
    print("ℹ️ FALLBACK MODE: Running without Gemini AI - using built-in intelligent responses")
    print("💡 NOTE: App works perfectly with advanced rule-based AI system")
    print("🤗 For Hugging Face: Add GOOGLE_API_KEY to your Space's environment variables")
print("=" * 60)