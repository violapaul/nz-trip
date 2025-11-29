#!/usr/bin/env python3
"""
Quick test script to verify Gemini API integration.

Usage:
    export GEMINI_API_KEY="your-key"
    python test_gemini.py
"""

import os
from google import genai

def test_gemini():
    api_key = os.environ.get('GEMINI_API_KEY')
    
    if not api_key:
        print("❌ GEMINI_API_KEY not set")
        print("\nSet it with:")
        print("  export GEMINI_API_KEY='your-key-here'")
        return False
    
    print(f"✓ API key found: {api_key[:10]}...")
    
    try:
        print("✓ Calling Gemini API...")
        client = genai.Client(api_key=api_key)
        
        response = client.models.generate_content(
            model="gemini-3-pro-preview",
            contents="Explain how AI works in 20 words or less",
        )
        
        print("✓ Response received!")
        print(f"\n{response.text}\n")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    success = test_gemini()
    exit(0 if success else 1)

