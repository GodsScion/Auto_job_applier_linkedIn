#!/usr/bin/env python3
"""
Quick test to verify AI configuration is working.
"""

import sys

def test_config():
    """Test the current AI configuration."""
    print("Testing AI Configuration...")
    
    try:
        # Import the configuration
        from config.secrets import use_AI, llm_api_url, llm_model, llm_api_key, ai_provider
        
        print(f"✓ AI Enabled: {use_AI}")
        print(f"✓ API URL: {llm_api_url}")
        print(f"✓ Model: {llm_model}")
        print(f"✓ API Key: {llm_api_key}")
        print(f"✓ Provider: {ai_provider}")
        
        if use_AI and llm_model == "llama3:latest":
            print("✓ Configuration looks correct!")
            return True
        else:
            print("✗ Configuration needs adjustment")
            return False
            
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False

def test_ollama_connection():
    """Test Ollama connection."""
    print("\nTesting Ollama connection...")
    
    try:
        import requests
        
        response = requests.get("http://127.0.0.1:11434/api/tags", timeout=5)
        
        if response.status_code == 200:
            models = response.json()
            print("✓ Ollama is running")
            model_names = [model.get('name', 'Unknown') for model in models.get('models', [])]
            print(f"✓ Available models: {model_names}")
            
            if "llama3:latest" in model_names:
                print("✓ Required model 'llama3:latest' is available")
                return True
            else:
                print("✗ Required model 'llama3:latest' not found")
                return False
        else:
            print(f"✗ Ollama error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Connection error: {e}")
        return False

def main():
    """Run the quick test."""
    print("Quick AI Configuration Test")
    print("=" * 40)
    
    config_ok = test_config()
    ollama_ok = test_ollama_connection()
    
    print("\n" + "=" * 40)
    if config_ok and ollama_ok:
        print("🎉 All tests passed! Your setup is ready.")
        print("\nYou can now run: python runAiBot.py")
        return 0
    else:
        print("❌ Some tests failed. Please check the configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
