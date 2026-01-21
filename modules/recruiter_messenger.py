'''
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

Copyright (C) 2024 Sai Vignesh Golla

License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html

GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

version:    26.01.18.23.30

Contributor: Sanjay Nainwal (sanjaynainwal129@gmail.com) - Feature: Recruiter Messaging
'''


# Imports
import csv
import os
from datetime import datetime
from typing import Literal

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time

from config.recruiter_messaging import *
from config.personals import first_name, last_name
from config.questions import years_of_experience
from modules.helpers import print_lg, buffer, make_directories

# Import AI functions conditionally
if use_ai_for_messages:
    from config.secrets import ai_provider, use_AI
    if use_AI:
        from modules.ai.openaiConnections import ai_answer_question
        from modules.ai.deepseekConnections import deepseek_answer_question
        from modules.ai.geminiConnections import gemini_answer_question


# Global variables
messages_sent_today = 0
messaged_recruiters = set()  # Track recruiter IDs to avoid duplicates


def _ensure_modal_closed(driver: WebDriver) -> None:
    '''
    Ensures any open message modal is closed to prevent stuck state.
    '''
    try:
        print_lg("🔒 Attempting to ensure all modals are closed...")
        # Multiple attempts to close any open modals
        for attempt in range(5):
            try:
                # First, try ESC key multiple times
                for _ in range(3):
                    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                    buffer(0.5)

                # Comprehensive list of close button selectors for LinkedIn modals
                close_selectors = [
                    # Message overlay modals
                    "//button[contains(@class, 'msg-overlay-bubble-header__control')]",
                    "//button[contains(@class, 'msg-overlay-bubble-header__close')]",
                    "//button[contains(@aria-label, 'Close message')]",
                    "//button[contains(@data-test-id, 'close-button')]",

                    # Artdeco modals
                    "//button[contains(@class, 'artdeco-modal__dismiss')]",
                    "//button[contains(@aria-label, 'Close')]",
                    "//button[contains(@aria-label, 'Dismiss')]",

                    # Generic close buttons
                    "//button[contains(@class, 'artdeco-button--circle') and contains(@aria-label, 'Close')]",
                    "//button[contains(@type, 'button') and contains(@aria-label, 'Close')]",

                    # Message-specific modals
                    "//div[contains(@class, 'msg-overlay-modal')]//button[contains(@aria-label, 'Close')]",
                    "//div[contains(@class, 'msg-form-modal')]//button[contains(@aria-label, 'Close')]",

                    # Overflow menu close
                    "//button[contains(@aria-label, 'Close menu')]",
                ]

                modal_closed = False
                # Skip extensive cleanup if dry run or minimal cleanup requested
                # Reduced attempts/waits for speed
                modal_closed = False
                for selector in close_selectors:
                    try:
                        # Use a very short wait for finding close buttons
                        close_btns = driver.find_elements(By.XPATH, selector)
                        if close_btns:
                           for close_btn in close_btns:
                                if close_btn.is_displayed():
                                    close_btn.click()
                                    buffer(0.5)
                                    modal_closed = True
                    except:
                        pass
                
                if modal_closed:
                    print_lg(f"Modal closed on attempt {attempt + 1}")
                    return

                # Handle "Discard draft" confirmation dialogs
                discard_selectors = [
                    "//button[contains(@class, 'artdeco-modal__confirm-btn')]",
                    "//button[contains(., 'Discard')]",
                    "//button[contains(@aria-label, 'Discard')]",
                    "//button[contains(text(), 'Discard draft')]"
                ]

                for selector in discard_selectors:
                    try:
                        discard_btns = driver.find_elements(By.XPATH, selector)
                        for discard_btn in discard_btns:
                            if discard_btn.is_displayed() and discard_btn.is_enabled():
                                discard_btn.click()
                                buffer(1)
                                modal_closed = True
                                break
                    except Exception:
                        continue

                # Check if any modals are still open by looking for modal backdrops
                try:
                    modal_backdrops = driver.find_elements(By.XPATH,
                        "//div[contains(@class, 'artdeco-modal') or contains(@class, 'msg-overlay') or contains(@class, 'modal-backdrop')]")
                    if not modal_backdrops:
                        break  # No more modals found
                except Exception:
                    break  # No modals found

                if modal_closed:
                    print_lg(f"Modal closed on attempt {attempt + 1}")
                    buffer(1)
                else:
                    buffer(1)  # Wait before next attempt

            except Exception as e:
                print_lg(f"Modal close attempt {attempt + 1} failed: {e}")
                buffer(1)
                continue

        # Final verification - try to detect any remaining message-related modals
        try:
            message_modals = driver.find_elements(By.XPATH,
                "//div[contains(@class, 'msg-connections-typeahead') or contains(@class, 'msg-form__contenteditable') or contains(@class, 'msg-overlay-modal')]")
            
            # Filter for only VISIBLE modals
            visible_modals = [m for m in message_modals if m.is_displayed()]
            
            if visible_modals:
                print_lg(f"⚠️ WARNING: {len(visible_modals)} visible message modal(s) may still be open, forcing additional close attempts")
                # Force close with JavaScript - more aggressive
                driver.execute_script("""
                    // Hide all modal overlays
                    var overlays = document.querySelectorAll('[class*="overlay"], [class*="backdrop"], [class*="modal"]');
                    for (var i = 0; i < overlays.length; i++) {
                        overlays[i].style.display = 'none';
                        overlays[i].style.visibility = 'hidden';
                        overlays[i].remove();
                    }

                    // Click all possible close buttons
                    var closeSelectors = [
                        'button[aria-label*="Close"]',
                        'button[aria-label*="Dismiss"]',
                        'button[class*="close"]',
                        'button[class*="dismiss"]',
                        'button[aria-label*="close"]',
                        'button[data-test-id*="close"]'
                    ];

                    for (var s = 0; s < closeSelectors.length; s++) {
                        var buttons = document.querySelectorAll(closeSelectors[s]);
                        for (var i = 0; i < buttons.length; i++) {
                            if (buttons[i].offsetParent !== null) {
                                buttons[i].click();
                            }
                        }
                    }

                    // Send ESC key multiple times
                    var escEvent = new KeyboardEvent('keydown', {key: 'Escape', keyCode: 27, which: 27, bubbles: true});
                    for (var i = 0; i < 5; i++) {
                        document.dispatchEvent(escEvent);
                    }
                """)
                buffer(3)
        except Exception as e:
            print_lg(f"❌ Final modal cleanup error: {e}")

    except Exception as e:
        print_lg(f"❌ Critical error in modal closing: {e}")

    # Final check - log any remaining modals
    try:
        remaining_modals = driver.find_elements(By.XPATH, "//div[contains(@class, 'artdeco-modal') or contains(@class, 'msg-overlay') or contains(@class, 'modal-backdrop')]")
        if remaining_modals:
            print_lg(f"⚠️ Warning: {len(remaining_modals)} modal(s) may still be present after cleanup attempts")
        else:
            print_lg("✅ Modal cleanup completed successfully - no modals detected")
    except Exception as e:
        print_lg(f"Error checking for remaining modals: {e}")


def find_recruiters_on_job_page(driver: WebDriver) -> list[dict]:
    '''
    Detects all potential messaging targets from the job posting page.
    Returns a list of dictionaries with recruiter/connection details.

    Returns list of:
    {
        'name': str,
        'title': str,
        'profile_link': str,
        'recruiter_id': str,
        'can_message': bool,
        'is_free_message': bool,  # True if free message, False if InMail required
        'button_type': str,  # 'message', 'connect', or 'none'
        'section': str  # 'hiring_team' or 'connections'
    }
    '''
    recruiters = []

    try:
        print_lg("Starting recruiter search...")

        # Ensure no modals are open from previous operations
        _ensure_modal_closed(driver)

        # STEP 1: Find "Meet the hiring team" section
        hiring_team_section = None
        try:
            hiring_team_header = driver.find_element(By.XPATH,
                "//h2[contains(@class, 'text-heading-medium') and contains(normalize-space(.), 'Meet the hiring team')]")
            hiring_team_section = hiring_team_header.find_element(By.XPATH,
                "./parent::div[contains(@class, 'artdeco-card')]")
            print_lg("Found 'Meet the hiring team' section")

            # Extract recruiter from hiring team section
            recruiter_info = _extract_recruiter_from_section(driver, hiring_team_section, 'hiring_team')
            if recruiter_info:
                recruiters.append(recruiter_info)

        except NoSuchElementException:
            print_lg("No 'Meet the hiring team' section found on this job posting.")

        # STEP 2: Find "People you can reach out to" section (always check, regardless of hiring team)
        try:
            connections_section = driver.find_element(By.XPATH,
                "//div[contains(@class, 'job-details-people-who-can-help__section--two-pane') and contains(@class, 'artdeco-card')]")
            print_lg("Found 'People you can reach out to' section")

            # Extract all connections from this section
            connections_list = find_connections_in_help_section(driver, connections_section)
            recruiters.extend(connections_list)

        except NoSuchElementException:
            print_lg("No 'People you can reach out to' section found on this job posting.")

        print_lg(f"Found {len(recruiters)} potential messaging targets")
        return recruiters

    except Exception as e:
        print_lg(f"Error finding recruiters: {e}")
        return []


def _extract_recruiter_from_section(driver: WebDriver, section: WebElement, section_type: str) -> dict | None:
    '''
    Extracts recruiter information from a given section (hiring team or connection card).
    '''
    recruiter_info = {'section': section_type}

    # STEP 1: Find profile link
    try:
        recruiter_link = section.find_element(By.XPATH, ".//a[contains(@href, '/in/')]")
        recruiter_info['profile_link'] = recruiter_link.get_attribute('href')

        # Extract recruiter ID from profile link
        try:
             recruiter_id = recruiter_info['profile_link'].split('/in/')[-1].split('/')[0].split('?')[0]
             recruiter_info['recruiter_id'] = recruiter_id
        except:
             recruiter_info['recruiter_id'] = "unknown"
    except NoSuchElementException:
        recruiter_info['profile_link'] = ""
        recruiter_info['recruiter_id'] = "unknown"

    # STEP 2: Find name
    try:
        if section_type == 'hiring_team':
            name_element = section.find_element(By.XPATH,
                ".//span[contains(@class, 'jobs-poster__name')]")
        else:  # connections section
            name_element = section.find_element(By.XPATH,
                ".//strong[contains(@class, 'EntityPhoto-circle-3-stackedFacepile')]")
        recruiter_info['name'] = name_element.text.strip()
    except NoSuchElementException:
        recruiter_info['name'] = "Unknown"

    # STEP 3: Find title
    try:
        if section_type == 'hiring_team':
            title_element = section.find_element(By.XPATH,
                ".//div[contains(@class, 'linked-area')]//div[contains(@class, 'text-body-small')]")
        else:  # connections section
            title_element = section.find_element(By.XPATH,
                ".//div[contains(@class, 'artdeco-entity-lockup__subtitle')]")
        recruiter_info['title'] = title_element.text.strip()
    except NoSuchElementException:
        recruiter_info['title'] = "Unknown Title"

    # STEP 4: Check message capability and button type
    message_capability = check_message_capability(driver, section)
    recruiter_info.update(message_capability)

    print_lg(f"Found {section_type} target: {recruiter_info['name']} ({recruiter_info['title']}) - "
            f"Button: {recruiter_info.get('button_type', 'none')}, Can Message: {recruiter_info['can_message']}, Free: {recruiter_info['is_free_message']}")

    return recruiter_info


def find_connections_in_help_section(driver: WebDriver, connections_section: WebElement) -> list[dict]:
    '''
    Extracts all connection targets from the "People you can reach out to" section.
    '''
    connections = []

    try:
        # Find all individual connection cards within the section
        connection_cards = connections_section.find_elements(By.XPATH,
            ".//div[contains(@class, 'artdeco-entity-lockup') and .//a[contains(@href, '/in/')]]")

        for card in connection_cards:
            recruiter_info = _extract_recruiter_from_section(driver, card, 'connections')
            if recruiter_info:
                connections.append(recruiter_info)

    except Exception as e:
        print_lg(f"Error extracting connections from help section: {e}")

    return connections


def check_message_capability(driver: WebDriver, section: WebElement) -> dict:
    '''
    Checks if target can be messaged and what type of interaction is available.

    Returns:
    {
        'can_message': bool,
        'is_free_message': bool,  # True if free, False if InMail/connect required
        'message_type': str,  # 'free', 'inmail', 'connection', 'connect', or 'unavailable'
        'button_type': str  # 'message', 'connect', or 'none'
    }
    '''
    result = {
        'can_message': False,
        'is_free_message': False,
        'message_type': 'unavailable',
        'button_type': 'none'
    }

    try:
        # STEP 1: Scan for ALL types of buttons first
        message_button = None
        connect_button = None
        
        try:
            message_button = section.find_element(By.XPATH,
                ".//button[contains(normalize-space(.), 'Message') or contains(@aria-label, 'Message')]")
            result['can_message'] = True
        except NoSuchElementException:
            pass
            
        try:
            connect_button = section.find_element(By.XPATH,
                ".//button[contains(normalize-space(.), 'Connect') or contains(@aria-label, 'Connect')]")
            result['can_message'] = True
        except NoSuchElementException:
            pass
            
        if not message_button and not connect_button:
            return result

        # STEP 2: Determine Connection Degree
        degree_text = ""
        try:
            connection_degree = section.find_element(By.XPATH, ".//span[contains(@class, 'hirer-card__connection-degree')]")
            degree_text = connection_degree.text.strip()
        except:
            pass

        # STEP 3: Prioritization Logic
        # Case A: 1st Degree Connection -> Always Message (Free)
        if '1st' in degree_text and message_button:
            result['button_type'] = 'message'
            result['is_free_message'] = True
            result['message_type'] = 'connection'
            return result

        # Case B: Connect Button Exists (2nd/3rd) -> Safer to use Connect + Note (Free)
        # We prioritize Connect over Message for non-1st because Message is often InMail
        if connect_button:
            result['button_type'] = 'connect'
            result['is_free_message'] = True
            result['message_type'] = 'connect'
            return result

        # Case C: Only Message Button Exists (2nd/3rd or Open Profile or InMail)
        if message_button:
            result['button_type'] = 'message'
            
            # Check for explicit premium/lock indicators on the button
            is_locked = False
            try:
                # 1. Check classes
                button_classes = message_button.get_attribute('class').lower()
                if 'premium' in button_classes or 'locked' in button_classes:
                    is_locked = True
                
                # 2. Check for lock icon SVG inside button
                if not is_locked:
                    try:
                        message_button.find_element(By.XPATH, ".//*[contains(@data-test-icon, 'lock')]")
                        is_locked = True
                    except:
                        pass
                
                # 3. Check aria-label for "InMail"
                if not is_locked:
                    aria_label = message_button.get_attribute('aria-label')
                    if aria_label and 'inmail' in aria_label.lower():
                        is_locked = True
            except:
                pass

            if is_locked:
                result['is_free_message'] = False
                result['message_type'] = 'inmail'
            else:
                # No lock detected -> Open Profile (Free)
                result['is_free_message'] = True 
                result['message_type'] = 'free'
                
            return result

        return result

    except Exception as e:
        print_lg(f"Error checking message capability: {e}")
        return result


def generate_personalized_message(
    aiClient,
    recruiter_info: dict,
    job_description: str,
    job_title: str,
    company_name: str,
    job_link: str
) -> tuple[str, str]:
    '''
    Generates a personalized message for the recruiter.
    Returns (subject, body) tuple.
    '''
    # Extract recruiter first name
    recruiter_name = recruiter_info.get('name', 'there').split()[0]
    your_name = f"{first_name} {last_name}"

    # Generate AI personalization if enabled
    personalized_intro = ""
    why_interested = ""

    if use_ai_for_messages and use_AI and aiClient:
        try:
            # Generate personalized intro
            intro_prompt = f"""Based on this job description, write a 2-sentence personalized introduction
explaining why the candidate is a good fit. Be specific about matching skills.

Job Title: {job_title}
Company: {company_name}
Job Description: {job_description[:500]}
Candidate Experience: {years_of_experience} years in backend development with Java"""

            if ai_provider.lower() == "openai":
                personalized_intro = ai_answer_question(aiClient, intro_prompt, question_type="text")
            elif ai_provider.lower() == "deepseek":
                personalized_intro = deepseek_answer_question(aiClient, intro_prompt, question_type="text")
            elif ai_provider.lower() == "gemini":
                personalized_intro = gemini_answer_question(aiClient, intro_prompt, question_type="text")

            # Generate why interested
            interest_prompt = f"""Write 1 sentence explaining why the candidate is interested in this role,
focusing on growth opportunity or company reputation.

Job Title: {job_title}
Company: {company_name}"""

            if ai_provider.lower() == "openai":
                why_interested = ai_answer_question(aiClient, interest_prompt, question_type="text")
            elif ai_provider.lower() == "deepseek":
                why_interested = deepseek_answer_question(aiClient, interest_prompt, question_type="text")
            elif ai_provider.lower() == "gemini":
                why_interested = gemini_answer_question(aiClient, interest_prompt, question_type="text")

            print_lg("AI-generated personalization completed")

        except Exception as e:
            print_lg(f"Failed to generate AI personalization: {e}")
            personalized_intro = ""
            why_interested = ""

    # Format subject
    subject = message_subject.format(
        job_title=job_title,
        company_name=company_name,
        recruiter_name=recruiter_name
    )

    # Format message body
    body = message_template.format(
        recruiter_name=recruiter_name,
        job_title=job_title,
        company_name=company_name,
        job_link=job_link,
        your_name=your_name,
        years_of_experience=years_of_experience,
        personalized_intro=personalized_intro,
        why_interested=why_interested,
        key_skills="Java, Spring Boot, Microservices"  # Can be made dynamic later
    ).strip()

    # Ensure message is within LinkedIn limits
    # Subject: 200 chars, Body: 1900 chars for regular messages
    if len(subject) > 200:
        subject = subject[:197] + "..."

    if len(body) > 1900:
        body = body[:1897] + "..."

    return subject, body


def send_message_to_recruiter(
    driver: WebDriver,
    recruiter_info: dict,
    subject: str,
    message_body: str
) -> tuple[bool, str]:
    '''
    Sends message to the recruiter via LinkedIn.
    Returns (success: bool, error_message: str)

    STEP 1: Capture initial state
    STEP 2: Click message button (may open inline modal OR new window)
    STEP 3: Detect messaging context (inline modal vs new window)
    STEP 4: Compose message in detected context
    STEP 5: Send message
    STEP 6: Cleanup - always execute
    '''
    global messages_sent_today

    if dry_run_mode:
        print_lg(f"[DRY RUN] Would send message to {recruiter_info['name']}")
        return True, "Dry run - message not actually sent"

    # STEP 1: Capture initial state
    original_window = driver.current_window_handle
    pre_click_handles = set(driver.window_handles)
    
    # Initialize variables for cleanup scope
    messaging_window_handle = None
    is_new_window = False

    # Ensure no stray modals are open from previous operations
    # CRITICAL: Close existing messaging bubbles to prevent 'full bar' issue
    # LinkedIn allows max 3-4 bubbles; if full, new Message click won't work
    # ALSO: Open bubbles can physically block the Message button click
    print_lg("🧹 Closing any existing messaging bubbles...")
    try:
        # Close conversation bubbles
        conversation_bubbles = driver.find_elements(By.XPATH,
            "//aside[contains(@class,'msg-overlay-conversation-bubble')]//button[contains(@aria-label,'Close')] | "
            "//*[contains(@class,'msg-overlay-conversation-bubble')]//button[contains(@aria-label,'Close')]")
        for bubble_close in conversation_bubbles[:5]:
            try:
                if bubble_close.is_displayed():
                    bubble_close.click()
                    buffer(0.3)
                    print_lg("✅ Closed a conversation bubble")
            except:
                pass
        
        # Close the messaging list bubble (this is what blocks clicks!)
        list_bubbles = driver.find_elements(By.XPATH,
            "//aside[contains(@class,'msg-overlay-list-bubble')]//button[contains(@aria-label,'Close')] | "
            "//*[contains(@class,'msg-overlay-list-bubble')]//button[contains(@aria-label,'Close')]")
        for bubble_close in list_bubbles[:3]:
            try:
                if bubble_close.is_displayed():
                    bubble_close.click()
                    buffer(0.3)
                    print_lg("✅ Closed a list bubble")
            except:
                pass
        
        # JavaScript fallback - force hide any remaining bubbles
        try:
            driver.execute_script("""
                // Hide all messaging overlays
                var bubbles = document.querySelectorAll('[class*="msg-overlay"]');
                for (var i = 0; i < bubbles.length; i++) {
                    if (bubbles[i].classList.contains('msg-overlay-list-bubble') || 
                        bubbles[i].classList.contains('msg-overlay-conversation-bubble')) {
                        bubbles[i].style.display = 'none';
                    }
                }
            """)
            print_lg("✅ JavaScript cleanup executed")
        except:
            pass
            
    except Exception as e:
        print_lg(f"⚠️ Bubble closing warning: {e}")
    
    _ensure_modal_closed(driver)
    buffer(1)

    # STEP 2: Click message/connect button
    try:
        current_name = recruiter_info.get('name', '').split()[0]
        
        # 2. Find button relative to the recruiter's name (Most Robust)
        # Instead of finding a container first (which might be too narrow, like just the <a> tag),
        # we search for a button that shares a common ancestor with the recruiter's name.
        
        print_lg(f"🔍 Searching for button anchored to name: '{current_name}'")
        search_context = driver # Use driver to avoid stale element issues
        
        # XPaths that find a button inside a container that ALSO contains the recruiter's name
        # This guarantees we click the button for THIS recruiter, not another one on the page
        btn_xpaths = []
        name_clean = current_name
        
        if recruiter_info['button_type'] == 'message':
            btn_xpaths = [
                # 1. Correct Structure: Button is sibling's child (entry-point sibling to hirer-card__hirer-information)
                # Find the container div that has BOTH the name text and a button descendant
                f"//div[contains(@class, 'display-flex') and .//*[contains(text(), '{name_clean}')]]//button[.//span[contains(text(), 'Message')]]",
                f"//div[contains(@class, 'display-flex') and .//*[contains(text(), '{name_clean}')]]//button[contains(normalize-space(.), 'Message')]",
                # 2. "Meet the hiring team" Section Fallback (Most Reliable)
                "//section[.//h2[contains(text(),'Meet the hiring team')]]//button[.//span[contains(text(), 'Message')]]",
                "//section[.//h2[contains(text(),'Meet the hiring team')]]//button[contains(normalize-space(.), 'Message')]",
                # 3. Artdeco card fallback
                f"//div[contains(@class,'artdeco-card') and .//*[contains(text(), '{name_clean}')]]//button[contains(normalize-space(.), 'Message')]",
            ]
        elif recruiter_info['button_type'] == 'connect':
            btn_xpaths = [
                 f"//div[contains(@class, 'display-flex') and .//*[contains(text(), '{name_clean}')]]//button[.//span[contains(text(), 'Connect')]]",
                 f"//div[contains(@class, 'display-flex') and .//*[contains(text(), '{name_clean}')]]//button[contains(normalize-space(.), 'Connect')]",
                 "//section[.//h2[contains(text(),'Meet the hiring team')]]//button[.//span[contains(text(), 'Connect')]]",
                 "//section[.//h2[contains(text(),'Meet the hiring team')]]//button[contains(normalize-space(.), 'Connect')]",
            ]
        else:
             btn_xpaths = ["//section[.//h2[contains(text(),'Meet the hiring team')]]//button[contains(normalize-space(.), 'Message')]"]

        action_button = None
        for path in btn_xpaths:
            try:
                action_button = driver.find_element(By.XPATH, path)
                print_lg(f"✅ Found button with anchored strategy: {path[:40]}...")
                break
            except: continue
            
        if not action_button:
             raise Exception(f"Could not find '{recruiter_info['button_type']}' button anchored to '{name_clean}'")

        print_lg(f"🖱️  Clicking {recruiter_info['button_type']} button (Safe Scope)...")
        
        # Scroll to ensure visibility
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", action_button)
        buffer(1)
        action_button.click()
        buffer(2)

        
    except Exception as e:
        return False, f"Failed to click {recruiter_info['button_type']} button: {e}"

    # STEP 3: Handle specific flows (Message vs Connect)
    
    # --- FLOW A: CONNECT WITH NOTE ---
    if recruiter_info['button_type'] == 'connect':
        try:
            print_lg("⏳ Waiting for Connect modal...")
            # Wait for the 'Add a note' modal
            modal_xpath = "//div[contains(@class, 'artdeco-modal') and contains(., 'Invite')]"
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, modal_xpath)))
            
            # Check if we need to click "Add a note"
            try:
                print_lg("�️  Clicking 'Add a note'...")
                add_note_btn = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Add a note')]")
                add_note_btn.click()
                buffer(1)
            except NoSuchElementException:
                # Does logic allow sending without note? Only if 'Add a note' is missing (already open?)
                print_lg("ℹ️ 'Add a note' button not found, checking if text area is already visible")

            # Type message
            print_lg("✍️  Typing connection note...")
            try:
                note_area = driver.find_element(By.ID, "custom-message")
                note_area.send_keys(message_body)
                buffer(1)
            except NoSuchElementException:
                return False, "Could not find custom message text area for connection"
            
            # Send (or Verify for Dry Run)
            try:
                send_btn = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Send invitation')]")
            except NoSuchElementException:
                return False, "Could not find 'Send invitation' button"
            
            if dry_run_mode:
                print_lg("✅ [DRY RUN] Would click 'Send invitation'")
                # Close modal to clean up
                try: driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Dismiss')]").click()
                except: pass
                return True, "Dry run - connection note not sent"
            
            print_lg("📤 Sending invitation...")
            send_btn.click()
            buffer(2)
            
            messages_sent_today += 1
            return True, "Connection request sent with note"
            
        except Exception as e:
            # Attempt to close any stuck modal
            try: driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Dismiss')]").click()
            except: pass
            return False, f"Failed in Connect flow: {e}"


    # --- FLOW B: REGULAR MESSAGE ---
    # Detect messaging context (New Window vs Inline Bubble)
    
    is_new_window = False
    messaging_window_handle = None
    
    # Check if a new window opened
    post_click_handles = set(driver.window_handles)
    if len(post_click_handles) > len(pre_click_handles):
        is_new_window = True
        new_handles = post_click_handles - pre_click_handles
        messaging_window_handle = list(new_handles)[0]
        driver.switch_to.window(messaging_window_handle)
        print_lg("switched to new messaging window")
        buffer(2)
    else:
        print_lg("Staying in main window (inline modal detected)")

    print_lg("⏳ Waiting for compose field to be fully rendered...")
    buffer(3)
    
    # STEP 4: Strict Verification of Conversation Context
    # User Requirement: "Don't just open new message window"
    # We enforce that the active bubble MUST contain the Recruiter's name.
    print_lg(f"🔍 Strictly verifying conversation context for {recruiter_info['name']}...")
    
    verified_context = False
    
    try:
        if is_new_window:
            # Logic for new window verification - wait for page load first
            buffer(2)  # Wait for new window content to fully load
            recruiter_first_name = recruiter_info['name'].split()[0].lower()
            page_source_lower = driver.page_source.lower()
            
            # Check if first name appears in page
            if recruiter_first_name in page_source_lower:
                verified_context = True
                print_lg(f"✅ Verified - Recruiter first name '{recruiter_first_name}' found in new window")
            else:
                # Try just first few characters (handles unicode/encoding issues)
                name_prefix = recruiter_first_name[:4]  # e.g., "gabr" for Gabriel
                if name_prefix in page_source_lower:
                    verified_context = True
                    print_lg(f"✅ Verified - Recruiter name prefix '{name_prefix}' found in new window")
                else:
                    # Check URL for profile indicator
                    if '/messaging/' in driver.current_url or '/in/' in driver.current_url:
                        print_lg(f"✅ Verified - Messaging URL detected, proceeding with message")
                        verified_context = True
                    else:
                        print_lg(f"⚠️ New window verification failed - name '{recruiter_first_name}' not found in page")
        else:
            # Inline Bubble Verification
            recruiter_first_name = recruiter_info['name'].split()[0]
            
            # 1. Wait for the NAME in any active message-related element (relaxed)
            verification_xpaths = [
                # Standard active bubble
                f"//*[contains(@class,'msg-overlay-conversation-bubble--is-active') or contains(@class,'msg-overlay-conversation-bubble--is-expanded') or contains(@class,'msg-overlay-conversation-bubble--is-compose')]//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{recruiter_first_name.lower()}')]",
                # Header in message overlay
                f"//*[contains(@class,'msg-overlay-bubble-header')]//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{recruiter_first_name.lower()}')]",
                # Any msg-convo container
                f"//*[contains(@class,'msg-convo-wrapper')]//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{recruiter_first_name.lower()}')]",
                # Generic: any element with 'msg' class containing the name
                f"//*[contains(@class,'msg-')]//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{recruiter_first_name.lower()}')]"
            ]
            
            for verification_xpath in verification_xpaths:
                try:
                    WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, verification_xpath)))
                    print_lg(f"✅ Verified - Recruiter name '{recruiter_first_name}' found in active conversation")
                    verified_context = True
                    break
                except TimeoutException:
                    continue

            # 2. Fallback: Check page source (less strict but prevents false aborts)
            if not verified_context:
                print_lg(f"⚠️ XPath Validation failed, checking page source...")
                if recruiter_first_name.lower() in driver.page_source.lower():
                    verified_context = True
                    print_lg(f"✅ Verified (Page Source) - Name '{recruiter_first_name}' found")
    
    except Exception as e:
        print_lg(f"⚠️ Verification check error: {e}")

    # FINAL DECISION: Abort if not verified
    if not verified_context:
         # Check for "New message" header which confirms it's a generic window
         try: 
             driver.find_element(By.XPATH, "//h2[contains(text(), 'New message')]")
             return False, "SAFETY ABORT: Generic 'New message' window detected (No Recipient)"
         except: pass
         
         return False, f"SAFETY ABORT: Could not verify that message window belongs to {recruiter_info['name']}"

    # STEP 4.5: POST-CLICK InMail Detection
    # Some recruiters show "Message" button but it actually requires InMail credits.
    # We detect this AFTER the click by checking for InMail-specific elements in the modal.
    print_lg(f"🔍 Checking if modal requires InMail credits...")
    is_inmail_modal = False
    
    try:
        # Check for InMail-specific indicators in the opened modal
        inmail_indicators = [
            # InMail credits display section (Most reliable)
            "//*[contains(@class,'msg-inmail-credits-display')]",
            # Text specifically mentioning InMail credits usage
            "//*[contains(text(),'InMail credit')]",
            "//*[contains(text(),'InMail credits')]",
            # Premium badge combined with non-free text
            "//section[contains(@class,'msg-inmail')]//svg[@aria-label='Premium']"
        ]
        
        for indicator in inmail_indicators:
            try:
                driver.find_element(By.XPATH, indicator)
                is_inmail_modal = True
                print_lg(f"⚠️ InMail detected via: {indicator[:60]}...")
                break
            except NoSuchElementException:
                continue
        
        if is_inmail_modal:
            print_lg(f"🚫 POST-CLICK InMail DETECTION: Modal requires InMail credits!")
            # Close this InMail modal before returning - try multiple methods
            modal_closed = False
            
            # Try multiple close button selectors
            close_button_xpaths = [
                # Close button by aria-label
                "//button[@aria-label='Close your draft conversation']",
                # Close button with close icon
                "//button[contains(@class,'msg-overlay-bubble-header__control')]//*[contains(@data-test-icon,'close')]/..",
                # Any close button in message header
                "//button[contains(@class,'msg-overlay-bubble-header__control') and .//span[contains(text(),'Close')]]",
                # Generic close with X icon in overlay
                "//*[contains(@class,'msg-overlay')]//button[.//*[contains(@data-test-icon,'close')]]"
            ]
            
            for close_xpath in close_button_xpaths:
                try:
                    close_btn = driver.find_element(By.XPATH, close_xpath)
                    close_btn.click()
                    buffer(0.5)
                    print_lg(f"✅ Closed InMail modal via: {close_xpath[:50]}...")
                    modal_closed = True
                    break
                except:
                    continue
            
            # JavaScript fallback if button clicks didn't work
            if not modal_closed:
                try:
                    driver.execute_script("""
                        var modals = document.querySelectorAll('.msg-overlay-conversation-bubble, .msg-inmail-compose-form-v2');
                        modals.forEach(function(m) { 
                            var closeBtn = m.querySelector('button[data-test-icon="close-small"], button[aria-label*="Close"]');
                            if(closeBtn) closeBtn.click();
                        });
                    """)
                    buffer(0.5)
                    print_lg("✅ Closed InMail modal via JavaScript")
                    modal_closed = True
                except Exception as js_err:
                    print_lg(f"⚠️ JS close also failed: {js_err}")
            
            if not modal_closed:
                print_lg("⚠️ Could not close InMail modal - will be cleaned up by next modal check")
            
            # Handle new window case
            if is_new_window and messaging_window_handle:
                driver.close()
                driver.switch_to.window(list(pre_click_handles)[0])
            
            return False, "SKIPPED: InMail required (detected post-click in modal)"
            
    except Exception as e:
        print_lg(f"⚠️ Post-click InMail check error (continuing): {e}")
    
    print_lg(f"✅ Modal is FREE message - no InMail credits required")
    
    # STEP 5: Compose message in detected context
    try:
        # Try multiple selectors for message body field (LinkedIn UI varies)
        msg_body = None
        body_selectors = [
            # Primary: Contenteditable INSIDE the active bubble (Most specific/safe)
            "//*[contains(@class,'msg-overlay-conversation-bubble--is-active') or contains(@class,'msg-overlay-conversation-bubble--is-expanded') or contains(@class,'msg-overlay-conversation-bubble--is-compose')]//div[contains(@class,'msg-form__contenteditable') and @contenteditable='true']",
            # Fallback 1: Generic msg-form contenteditable
            "//div[@contenteditable='true' and contains(@class,'msg-form')]",
            # Fallback 2: Any contenteditable in message context
            "//div[@contenteditable='true' and contains(@class,'message')]",
            # Fallback 3: Most generic
            "//div[@contenteditable='true' and @role='textbox']"
        ]
        
        for selector in body_selectors:
            try:
                msg_body = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                print_lg(f"✅ Found message body with selector: {selector[:50]}...")
                break
            except:
                continue
        
        if not msg_body:
            return False, "ERROR: Message body field not found with any selector"
        
        # Ensure field is focused and ready
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", msg_body)
        driver.execute_script("arguments[0].focus();", msg_body)
        buffer(0.5)
        
        # Clear existing content first
        driver.execute_script("""
            var field = arguments[0];
            field.innerHTML = '';
            field.dispatchEvent(new Event('input', { bubbles: true }));
        """, msg_body)
        buffer(0.3)
        
        # Try multiple text insertion methods for maximum compatibility
        text_inserted = False
        
        # Method 1: JavaScript innerHTML with proper event triggering
        try:
            driver.execute_script("""
                var field = arguments[0];
                var text = arguments[1];
                var p = document.createElement('p');
                p.textContent = text;
                field.appendChild(p);
                field.dispatchEvent(new Event('input', { bubbles: true }));
                field.dispatchEvent(new Event('change', { bubbles: true }));
            """, msg_body, message_body)
            buffer(0.5)
            entered_text = msg_body.get_attribute('innerText').strip()
            if len(entered_text) >= 10:
                text_inserted = True
                print_lg("Text inserted via JavaScript method")
        except Exception as e:
            print_lg(f"JavaScript insertion failed: {e}")
        
        # Method 2: Fallback - Selenium send_keys
        if not text_inserted:
            try:
                msg_body.clear()
                msg_body.send_keys(message_body)
                buffer(0.5)
                entered_text = msg_body.get_attribute('innerText').strip()
                if len(entered_text) >= 10:
                    text_inserted = True
                    print_lg("Text inserted via send_keys fallback")
            except Exception as e:
                print_lg(f"send_keys fallback failed: {e}")
        
        # Verify text was inserted
        entered_text = msg_body.get_attribute('innerText').strip()
        if len(entered_text) < 10:
            return False, f"ERROR: Text insertion failed - only {len(entered_text)} characters inserted"
        
        print_lg(f"✅ Successfully inserted {len(entered_text)} characters")
        
    except Exception as e:
        return False, f"ERROR: Failed to fill message fields - {str(e)}"
    
    # STEP 5: Send message
    try:
        # Try multiple send button selectors (LinkedIn UI varies)
        send_button = None
        send_selectors = [
            # Primary: msg-form__send-button
            "//button[contains(@class,'msg-form__send-button') and not(@disabled)]",
            # Fallback 1: msg-form with send
            "//button[contains(@class,'msg-form') and contains(@class,'send') and not(@disabled)]",
            # Fallback 2: Just send button with aria-label
            "//button[contains(@aria-label,'Send') and not(@disabled)]",
            # Fallback 3: Any button with 'Send' text
            "//button[contains(normalize-space(.),'Send') and not(@disabled)]",
            # Fallback 4: submit type button
            "//button[@type='submit' and not(@disabled)]"
        ]
        
        for selector in send_selectors:
            try:
                send_button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                print_lg(f"✅ Found send button with selector: {selector[:50]}...")
                break
            except:
                continue
        
        if not send_button:
            return False, "ERROR: Send button not found with any selector"
        
        # DRY RUN CHECK: Don't actually click send if in dry run mode
        if dry_run_mode:
            print_lg(f"✅ [DRY RUN] Would click 'Send' for {recruiter_info['name']}")
            _ensure_modal_closed(driver)
            return True, "Dry run - message not sent"
        
        send_button.click()
        buffer(3)  # Wait for send confirmation
        
        # Verify message was sent by checking if modal/compose area is gone
        send_verified = False
        for _ in range(5):
            try:
                # If we can't find the message body anymore, send likely succeeded
                driver.find_element(By.XPATH, "//div[contains(@class,'msg-form__contenteditable')]")
                buffer(1)  # Still there, wait more
            except NoSuchElementException:
                send_verified = True
                break
        
        if send_verified:
            print_lg(f"✅ Message sent and verified for {recruiter_info['name']}")
        else:
            print_lg(f"⚠️ Message clicked send for {recruiter_info['name']} but modal still visible")
        
        messages_sent_today += 1
        messaged_recruiters.add(recruiter_info['recruiter_id'])
        
        return True, ""
        
    except Exception as e:
        return False, f"ERROR: Failed to send message - {str(e)}"
    
    except Exception as e:
        error_msg = f"Failed to send message: {str(e)}"
        print_lg(error_msg)
        return False, error_msg
    
    finally:
        # STEP 6: Cleanup - always execute
        try:
            if is_new_window and messaging_window_handle in driver.window_handles:
                driver.close()
                driver.switch_to.window(original_window)
                print_lg("✅ Closed messaging window and returned to original")
            else:
                # Close inline modal if it exists
                try:
                    close_btn = driver.find_element(By.XPATH,
                        "//button[@aria-label='Close' or contains(@class,'close-modal')]")
                    close_btn.click()
                    buffer(1)
                except:
                    pass  # Modal already closed, ignore
                    
                _ensure_modal_closed(driver)
        except Exception as e:
            print_lg(f"Error in cleanup: {e}")





def track_sent_message(
    job_id: str,
    job_title: str,
    company_name: str,
    job_link: str,
    recruiter_info: dict,
    subject: str,
    message_body: str,
    success: bool,
    skip_reason: str = "",
    error_message: str = ""
) -> None:
    '''
    Records sent message or skip reason in CSV file.
    '''
    try:
        # Ensure directory exists
        make_directories([message_history_file])

        # Determine message type
        if recruiter_info.get('is_free_message'):
            if recruiter_info.get('message_type') == 'connection':
                msg_type = "Free (1st Connection)"
            else:
                msg_type = "Free Message"
        else:
            msg_type = "Skipped - InMail Required"

        # Determine success status
        if skip_reason:
            status = "Skipped"
        elif success:
            status = "Sent"
        else:
            status = "Failed"

        # Prepare row data
        row = [
            job_id,
            job_title,
            company_name,
            job_link,
            recruiter_info.get('name', 'Unknown'),
            recruiter_info.get('title', 'Unknown'),
            recruiter_info.get('profile_link', ''),
            msg_type,
            subject,
            message_body,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            status,
            skip_reason,
            error_message
        ]

        # Check if file exists to determine if we need headers
        file_exists = os.path.exists(message_history_file)

        # Write to CSV
        with open(message_history_file, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            # Write header if new file
            if not file_exists:
                headers = [
                    'Job ID', 'Job Title', 'Company', 'Job Link',
                    'Recruiter Name', 'Recruiter Title', 'Recruiter Profile Link',
                    'Message Type', 'Subject', 'Message Body', 'Date Sent',
                    'Status', 'Skip Reason', 'Error Message'
                ]
                writer.writerow(headers)

            writer.writerow(row)

        print_lg(f"Tracking record saved for {recruiter_info.get('name', 'Unknown')}")

    except Exception as e:
        print_lg(f"Failed to track message: {e}")


def check_daily_message_limit() -> bool:
    '''
    Checks if daily message limit has been reached.
    Returns True if limit reached, False otherwise.
    '''
    global messages_sent_today

    if messages_sent_today >= max_messages_per_day:
        print_lg(f"⚠️ Daily message limit reached ({max_messages_per_day}). Stopping message sending.")
        return True

    return False


def should_skip_recruiter(recruiter_info: dict, job_id: str, already_applied: bool) -> tuple[bool, str]:
    '''
    Determines if recruiter should be skipped.
    Returns (should_skip: bool, reason: str)
    '''
    # Check if already messaged this recruiter
    if recruiter_info['recruiter_id'] in messaged_recruiters:
        return True, "Already messaged this recruiter today"

    # Check if already applied to job
    if skip_if_already_applied and already_applied:
        return True, "Already applied via Easy Apply"

    # Check if InMail required but we want only free messages
    if skip_inmail_required and not recruiter_info['is_free_message']:
        return True, "InMail required (preserving credits)"

    # Check daily limit
    if check_daily_message_limit():
        return True, "Daily message limit reached"

    # Check if can message at all
    if not recruiter_info['can_message']:
        return True, "No message button available"

    return False, ""
