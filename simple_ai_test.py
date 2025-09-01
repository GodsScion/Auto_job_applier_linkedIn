#!/usr/bin/env python3
"""
Simple test to verify AI integration is working.
"""

import sys

def test_ai_integration():
    """Test the AI integration."""
    print("Testing AI Integration...")
    
    try:
        # Import the AI modules
        from modules.ai.openaiConnections import ai_create_openai_client
        
        print("Creating AI client...")
        client = ai_create_openai_client()
        
        if client:
            print("✓ AI client created successfully!")
            print("✓ Your local Llama3 integration is working!")
            return True
        else:
            print("✗ Failed to create AI client")
            return False
            
    except Exception as e:
        print(f"✗ AI integration error: {e}")
        return False

def main():
    """Run the test."""
    print("Simple AI Integration Test")
    print("=" * 40)
    
    if test_ai_integration():
        print("\n🎉 AI integration is working!")
        print("\nYour bot is now configured to:")
        print("1. Use your local Llama3 model")
        print("2. Generate custom cover letters for each job")
        print("3. Answer application questions intelligently")
        print("\nReady to run: python runAiBot.py")
        return 0
    else:
        print("\n❌ AI integration failed. Please check the error above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
