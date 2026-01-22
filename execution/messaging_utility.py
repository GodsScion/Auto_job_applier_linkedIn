'''
Messaging Utility for LinkedIn
Standalone tool to send personalized messages to recruiters and connections.

Author: Auto Job Applier Team
'''

# Imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.secrets import username, password, ai_provider, use_AI
from config.settings import *
from config.recruiter_messaging import *
from modules.open_chrome import *
from modules.helpers import print_lg, buffer
from modules.recruiter_messenger import (
    generate_personalized_message,
    send_message_to_recruiter,
    track_sent_message,
    check_daily_message_limit
)

# Import AI conditionally
if use_AI:
    if ai_provider.lower() == "openai":
        from modules.ai.openaiConnections import ai_create_openai_client
    elif ai_provider.lower() == "deepseek":
        from modules.ai.deepseekConnections import deepseek_create_client
    elif ai_provider.lower() == "gemini":
        from modules.ai.geminiConnections import gemini_create_client

def try_linkText(driver, text):
    try:
        return driver.find_element(By.LINK_TEXT, text)
    except:
        return None

def try_xp(driver, xpath, timeout=1):
    try:
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
        return driver.find_element(By.XPATH, xpath)
    except:
        return None

def is_logged_in_LN(driver) -> bool:
    """Check if logged into LinkedIn"""
    print_lg("Checking login status...")
    current_url = driver.current_url
    print_lg(f"Current URL: {current_url}")
    if driver.current_url == "https://www.linkedin.com/feed/":
        print_lg("Login detected: On feed page.")
        return True
    if try_linkText(driver, "Sign in"):
        print_lg("Login check failed: Found 'Sign in' link.")
        return False
    if try_xp(driver, '//button[@type="submit" and contains(text(), "Sign in")]'):
        print_lg("Login check failed: Found 'Sign in' button.")
        return False
    if try_linkText(driver, "Join now"):
        print_lg("Login check failed: Found 'Join now' link.")
        return False
    print_lg("Didn't find Sign in link/button, assuming user is logged in!")
    return True

def login_LN(driver) -> bool:
    """Login to LinkedIn"""
    try:
        driver.get("https://www.linkedin.com/login")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )

        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")

        username_field.send_keys(username)
        password_field.send_keys(password)

        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()

        # Wait for login to complete
        time.sleep(5)  # Initial wait for login attempt

        if is_logged_in_LN(driver):
            print_lg("Login successful!")
            return True
        else:
            print_lg("Login appears to have failed or is taking longer. Please complete the login manually in the browser if needed.")
            input("Press Enter after confirming login is complete...")
            if is_logged_in_LN(driver):
                print_lg("Login confirmed!")
                return True
            else:
                print_lg("Login still not confirmed.")
                return False

    except Exception as e:
        print_lg(f"Login failed: {e}")
        return False

def find_people_to_message(driver, search_keywords: list) -> list[dict]:
    """Find people from search results"""
    people = []

    try:
        for keyword in search_keywords:
            print_lg(f"Searching for people with keyword: {keyword}")

            # Go to people search
            search_url = f"https://www.linkedin.com/search/results/people/?keywords={keyword}"
            driver.get(search_url)
            time.sleep(3)

            # Get people from results
            person_cards = driver.find_elements(By.XPATH,
                "//div[contains(@class, 'entity-result__item')]"
            )[:10]  # Limit to 10 per keyword

            for card in person_cards:
                try:
                    name_elem = card.find_element(By.XPATH, ".//span[contains(@class, 'entity-result__title-text')]//a")
                    name = name_elem.text.strip()
                    profile_link = name_elem.get_attribute('href').split('?')[0]

                    # Get title/occupation
                    try:
                        title_elem = card.find_element(By.XPATH, ".//div[contains(@class, 'entity-result__primary-subtitle')]")
                        title = title_elem.text.strip()
                    except:
                        title = "Professional"

                    # Check if connect/message possible
                    try:
                        connect_btn = card.find_element(By.XPATH, ".//button[contains(@aria-label, 'Invite')]")
                        can_message = True
                        button_type = 'connect'
                    except:
                        try:
                            message_btn = card.find_element(By.XPATH, ".//button[contains(@aria-label, 'Message')]")
                            can_message = True
                            button_type = 'message'
                        except:
                            can_message = False
                            button_type = 'none'

                    if can_message:
                        person_info = {
                            'name': name,
                            'title': title,
                            'profile_link': profile_link,
                            'recruiter_id': profile_link.split('/in/')[-1].split('/')[0],
                            'can_message': True,
                            'is_free_message': True,  # Assume free for search results
                            'button_type': button_type,
                            'section': 'search_results'
                        }
                        people.append(person_info)
                        print_lg(f"Found: {name} - {title}")

                except Exception as e:
                    print_lg(f"Error parsing person card: {e}")
                    continue

    except Exception as e:
        print_lg(f"Error in people search: {e}")

    return people

def send_bulk_messages(driver, people_list: list[dict], ai_client=None) -> None:
    """Send messages to list of people"""
    global messages_sent_today

    for person in people_list:
        if check_daily_message_limit():
            print_lg("Daily message limit reached. Stopping.")
            break

        print_lg(f"\n--- Processing {person['name']} ---")

        # Generate personalized message
        subject, message_body = generate_personalized_message(
            ai_client,
            person,
            "",  # No job description for general messaging
            "Networking Opportunity",  # Generic job title
            "Professional Network",  # Generic company
            person.get('profile_link', '')
        )

        # Send message
        success, error_msg = send_message_to_recruiter(
            driver, person, subject, message_body
        )

        # Track result
        track_sent_message(
            "bulk_messaging",  # Generic job ID
            "Bulk Messaging",
            "Various Companies",
            "https://www.linkedin.com/search/results/people/",
            person, subject, message_body, success, "", error_msg
        )

        if success:
            messages_sent_today += 1
            print_lg(f"✅ Message sent to {person['name']}")
        else:
            print_lg(f"❌ Failed to message {person['name']}: {error_msg}")

        # Respect delays
        buffer(message_delay_seconds)

def main():
    """Main execution function"""
    global messages_sent_today

    print_lg("=== LinkedIn Messaging Utility ===")
    print_lg(f"Start Time: {datetime.now()}")

    # Initialize AI client
    ai_client = None
    if use_AI:
        try:
            if ai_provider.lower() == "openai":
                ai_client = ai_create_openai_client()
            elif ai_provider.lower() == "deepseek":
                ai_client = deepseek_create_client()
            elif ai_provider.lower() == "gemini":
                ai_client = gemini_create_client()
            print_lg(f"AI client initialized: {ai_provider}")
        except Exception as e:
            print_lg(f"Failed to initialize AI client: {e}")

    # Setup browser - already initialized by import
    try:
        print_lg("Browser initialized")
    except Exception as e:
        print_lg(f"Failed to setup browser: {e}")
        return

    try:
        # Login
        if not is_logged_in_LN(driver):
            if not login_LN(driver):
                print_lg("Login failed. Exiting.")
                return

        # Search keywords for finding people
        search_keywords = [
            "software engineer",
            "product manager",
            "recruiter",
            "hiring manager"
        ]  # Can be made configurable

        # Find people to message
        people_to_message = find_people_to_message(driver, search_keywords)
        print_lg(f"Found {len(people_to_message)} people to message")

        if not people_to_message:
            print_lg("No people found to message. Exiting.")
            return

        # Send messages
        send_bulk_messages(driver, people_to_message, ai_client)

    except Exception as e:
        print_lg(f"Error in main execution: {e}")
    finally:
        # Cleanup
        try:
            if driver:
                driver.quit()
            print_lg("Browser closed")
        except:
            pass

    print_lg(f"Total messages sent today: {messages_sent_today}")
    print_lg("Messaging utility completed.")

if __name__ == "__main__":
    main()