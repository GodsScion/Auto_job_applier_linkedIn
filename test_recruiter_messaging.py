#!/usr/bin/env python3
"""
Standalone Test Script for Recruiter Messaging

This script allows you to manually test the recruiter messaging functionality
on a single LinkedIn job posting. It includes enhanced logging to help debug
any issues with the messaging flow.

Usage:
    python test_recruiter_messaging.py

Instructions:
    1. Run this script
    2. When the browser opens, manually navigate to a job posting
    3. Press Enter in the terminal when you're on the job page
    4. The script will attempt to find and message recruiters
"""

import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

from modules.recruiter_messenger import (
    find_recruiters_on_job_page,
    generate_personalized_message,
    send_message_to_recruiter
)
from modules.helpers import print_lg
from config.recruiter_messaging import dry_run_mode, use_ai_for_messages
from config.secrets import use_AI, ai_provider

def setup_browser():
    """Setup Chrome browser with options similar to the main bot"""
    print_lg("🌐 Setting up browser...")
    
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Use your existing Chrome profile to maintain login session
    # Uncomment and modify the path below if you want to use your profile
    # chrome_options.add_argument("user-data-dir=/Users/sanju/Library/Application Support/Google/Chrome")
    # chrome_options.add_argument("profile-directory=Default")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver

def main():
    """Main test function"""
    print_lg("=" * 80)
    print_lg("RECRUITER MESSAGING TEST SCRIPT")
    print_lg("=" * 80)
    print_lg("")
    print_lg(f"Dry Run Mode: {dry_run_mode}")
    print_lg(f"AI Messages Enabled: {use_ai_for_messages and use_AI}")
    if use_ai_for_messages and use_AI:
        print_lg(f"AI Provider: {ai_provider}")
    print_lg("")
    
    driver = None
    aiClient = None
    
    try:
        # Setup browser
        driver = setup_browser()
        
        # Setup AI client if needed
        if use_ai_for_messages and use_AI:
            print_lg("🤖 Setting up AI client...")
            if ai_provider.lower() == "openai":
                from modules.ai.openaiConnections import get_openai_client
                aiClient = get_openai_client()
            elif ai_provider.lower() == "deepseek":
                from modules.ai.deepseekConnections import get_deepseek_client
                aiClient = get_deepseek_client()
            elif ai_provider.lower() == "gemini":
                from modules.ai.geminiConnections import get_gemini_client
                aiClient = get_gemini_client()
        
        # Navigate to LinkedIn
        print_lg("📱 Opening LinkedIn...")
        driver.get("https://www.linkedin.com")
        
        print_lg("")
        print_lg("=" * 80)
        print_lg("MANUAL STEP REQUIRED")
        print_lg("=" * 80)
        print_lg("1. If not logged in, please log in to LinkedIn")
        print_lg("2. Navigate to a job posting that has a 'Meet the hiring team' section")
        print_lg("3. Once you're on the job page, come back here and press Enter")
        print_lg("=" * 80)
        input("Press Enter when you're ready to continue...")
        
        # Get current URL for logging
        current_url = driver.current_url
        print_lg(f"📍 Current URL: {current_url}")
        
        # Extract job ID from URL if possible
        job_id = "manual_test"
        if "/jobs/view/" in current_url:
            try:
                job_id = current_url.split("/jobs/view/")[1].split("/")[0].split("?")[0]
                print_lg(f"🆔 Job ID: {job_id}")
            except:
                pass
        
        print_lg("")
        print_lg("=" * 80)
        print_lg("STEP 1: Finding Recruiters")
        print_lg("=" * 80)
        
        # Find recruiters
        recruiters = find_recruiters_on_job_page(driver)
        
        if not recruiters:
            print_lg("❌ No recruiters found on this page")
            print_lg("   Make sure you're on a job posting with a 'Meet the hiring team' section")
            return
        
        print_lg(f"✅ Found {len(recruiters)} potential messaging target(s)")
        print_lg("")
        
        # Display found recruiters
        for i, recruiter in enumerate(recruiters, 1):
            print_lg(f"  {i}. {recruiter['name']} ({recruiter['title']})")
            print_lg(f"     Section: {recruiter['section']}")
            print_lg(f"     Can Message: {recruiter['can_message']}")
            print_lg(f"     Free Message: {recruiter['is_free_message']}")
            print_lg(f"     Button Type: {recruiter['button_type']}")
            print_lg("")
        
        # Filter to messageable recruiters
        messageable = [r for r in recruiters if r['can_message'] and r['is_free_message']]
        
        if not messageable:
            print_lg("❌ No recruiters with free messaging available")
            print_lg("   (All require InMail or connection)")
            return
        
        print_lg("=" * 80)
        print_lg("STEP 2: Selecting Recruiter to Message")
        print_lg("=" * 80)
        
        # Use the first messageable recruiter
        target_recruiter = messageable[0]
        print_lg(f"🎯 Selected: {target_recruiter['name']}")
        print_lg("")
        
        print_lg("=" * 80)
        print_lg("STEP 3: Generating Message")
        print_lg("=" * 80)
        
        # Get job details from page
        try:
            job_title = driver.find_element("xpath", "//h1[contains(@class, 'job-title')]").text
        except:
            job_title = "Software Engineer"
        
        try:
            company_name = driver.find_element("xpath", "//a[contains(@class, 'job-card-container__company-name')]").text
        except:
            company_name = "the company"
        
        job_description = "Test job description"
        
        # Generate message
        subject, body = generate_personalized_message(
            aiClient,
            target_recruiter,
            job_description,
            job_title,
            company_name,
            current_url
        )
        
        print_lg(f"📧 Subject: {subject}")
        print_lg(f"📝 Message Preview:")
        print_lg("-" * 80)
        print_lg(body[:300] + "..." if len(body) > 300 else body)
        print_lg("-" * 80)
        print_lg("")
        
        if dry_run_mode:
            print_lg("🏃 DRY RUN MODE: Would send message but not actually sending")
            print_lg("   Set dry_run_mode = False in config/recruiter_messaging.py to send real messages")
            return
        
        print_lg("=" * 80)
        print_lg("STEP 4: Sending Message")
        print_lg("=" * 80)
        print_lg("⚠️  About to send a real message!")
        print_lg("")
        response = input("Type 'YES' to proceed with sending the message, or anything else to cancel: ")
        
        if response.strip().upper() != "YES":
            print_lg("❌ Cancelled by user")
            return
        
        print_lg("")
        print_lg("📤 Sending message...")
        print_lg("-" * 80)
        
        # Send message
        success, error_msg = send_message_to_recruiter(
            driver,
            target_recruiter,
            subject,
            body
        )
        
        print_lg("-" * 80)
        print_lg("")
        
        if success:
            print_lg("✅ SUCCESS! Message sent successfully")
        else:
            print_lg(f"❌ FAILED: {error_msg}")
        
        print_lg("")
        print_lg("=" * 80)
        print_lg("Test Complete")
        print_lg("=" * 80)
        print_lg("Browser will remain open for 30 seconds so you can verify...")
        time.sleep(30)
        
    except KeyboardInterrupt:
        print_lg("\n⚠️  Test interrupted by user")
    except Exception as e:
        print_lg(f"\n❌ Error during test: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            print_lg("🔒 Closing browser...")
            driver.quit()

if __name__ == "__main__":
    main()
