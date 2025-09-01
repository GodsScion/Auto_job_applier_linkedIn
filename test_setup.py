#!/usr/bin/env python3
"""
Test script to verify the LinkedIn Auto Job Applier setup is working correctly.
"""

import sys
import os

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        # Test basic imports
        import csv
        import re
        import pyautogui
        from random import choice, shuffle, randint
        from datetime import datetime
        print("✓ Basic Python modules imported successfully")
        
        # Test Selenium imports
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support.select import Select
        from selenium.webdriver.remote.webelement import WebElement
        from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, NoSuchWindowException, ElementNotInteractableException, WebDriverException
        print("✓ Selenium modules imported successfully")
        
        # Test configuration imports
        import config.personals
        import config.questions
        import config.search
        import config.secrets
        import config.settings
        print("✓ Configuration modules imported successfully")
        
        # Test custom module imports
        import modules.open_chrome
        import modules.helpers
        import modules.clickers_and_finders
        import modules.validator
        print("✓ Custom modules imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error during imports: {e}")
        return False

def test_configuration():
    """Test that configuration files are properly set up."""
    print("\nTesting configuration...")
    
    try:
        # Test that required variables are defined
        from config.personals import first_name, last_name, phone_number
        from config.questions import years_of_experience, require_visa
        from config.search import search_terms, search_location
        from config.settings import file_name, failed_file_name
        
        print(f"✓ Personal info: {first_name} {last_name}")
        print(f"✓ Phone: {phone_number}")
        print(f"✓ Experience: {years_of_experience} years")
        print(f"✓ Visa sponsorship: {require_visa}")
        print(f"✓ Search terms: {search_terms}")
        print(f"✓ Search location: {search_location}")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False

def test_directories():
    """Test that required directories exist."""
    print("\nTesting directories...")
    
    required_dirs = [
        "all resumes/default",
        "all excels", 
        "logs/screenshots"
    ]
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✓ Directory exists: {dir_path}")
        else:
            print(f"✗ Directory missing: {dir_path}")
            return False
    
    return True

def main():
    """Run all tests."""
    print("LinkedIn Auto Job Applier - Setup Test")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_configuration),
        ("Directory Test", test_directories)
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
        print("🎉 All tests passed! Your setup is ready to use.")
        print("\nNext steps:")
        print("1. Update your personal information in config/personals.py")
        print("2. Update your LinkedIn credentials in config/secrets.py")
        print("3. Add your resume to 'all resumes/default/resume.pdf'")
        print("4. Run 'python runAiBot.py' to start the bot")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
