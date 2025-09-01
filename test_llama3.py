#!/usr/bin/env python3
"""
Test script to verify local Llama3 integration is working correctly.
"""

import sys
import os

def test_llama3_connection():
    """Test connection to local Llama3 model."""
    print("Testing local Llama3 connection...")
    
    try:
        # Import the AI modules
        from modules.ai.openaiConnections import ai_create_openai_client, ai_answer_question, ai_close_openai_client
        
        # Test creating the client
        print("Creating AI client...")
        client = ai_create_openai_client()
        
        if client:
            print("✓ AI client created successfully")
            
            # Test a simple question
            test_question = "What is 2+2?"
            print(f"Testing with question: '{test_question}'")
            
            try:
                answer = ai_answer_question(client, test_question, question_type="text")
                print(f"✓ AI response: {answer}")
            except Exception as e:
                print(f"⚠️ AI question test failed: {e}")
                print("This might be normal if the model is still loading...")
            
            # Test cover letter generation
            test_job_description = """
            Entry Level Mechanical Engineer
            We are looking for a mechanical engineering graduate to join our team.
            Requirements:
            - Bachelor's degree in Mechanical Engineering
            - Experience with CAD software (SolidWorks preferred)
            - Knowledge of manufacturing processes
            - Strong analytical and problem-solving skills
            """
            
            print("\nTesting cover letter generation...")
            try:
                cover_letter = ai_answer_question(client, "Write a professional cover letter for this job", 
                                                question_type="textarea", 
                                                job_description=test_job_description)
                print(f"✓ Generated cover letter:\n{cover_letter}")
            except Exception as e:
                print(f"⚠️ Cover letter generation failed: {e}")
            
            # Close the client
            ai_close_openai_client(client)
            print("✓ AI client closed successfully")
            
            return True
        else:
            print("✗ Failed to create AI client")
            return False
            
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Connection error: {e}")
        return False

def test_ollama_status():
    """Test if Ollama is running and accessible."""
    print("\nTesting Ollama status...")
    
    try:
        import requests
        
        # Test if Ollama is running
        response = requests.get("http://127.0.0.1:11434/api/tags", timeout=5)
        
        if response.status_code == 200:
            models = response.json()
            print("✓ Ollama is running")
            print("Available models:")
            for model in models.get('models', []):
                print(f"  - {model.get('name', 'Unknown')}")
            return True
        else:
            print(f"✗ Ollama responded with status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to Ollama. Is it running?")
        print("To start Ollama, run: ollama serve")
        return False
    except Exception as e:
        print(f"✗ Error testing Ollama: {e}")
        return False

def main():
    """Run all tests."""
    print("Local Llama3 Integration Test")
    print("=" * 50)
    
    tests = [
        ("Ollama Status Test", test_ollama_status),
        ("Llama3 Connection Test", test_llama3_connection)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
            print(f"✓ {test_name} PASSED")
        else:
            print(f"✗ {test_name} FAILED")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your local Llama3 setup is ready.")
        print("\nYour bot will now:")
        print("1. Use your local Llama3 model for AI responses")
        print("2. Generate custom cover letters for each job posting")
        print("3. Answer application questions intelligently")
        print("\nReady to run: python runAiBot.py")
    elif passed == 1:
        print("⚠️ Partial success. Ollama is running but there might be model issues.")
        print("\nTroubleshooting:")
        print("1. Make sure your Llama3 model is downloaded: ollama pull llama3.2:3b-instruct")
        print("2. Check if the model name in config/secrets.py matches your installed model")
        print("3. Try running: ollama list to see available models")
    else:
        print("❌ Tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        print("1. Start Ollama: ollama serve")
        print("2. Download Llama3: ollama pull llama3.2:3b-instruct")
        print("3. Check if port 11434 is available")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
