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
                for selector in close_selectors:
                    try:
                        close_btns = driver.find_elements(By.XPATH, selector)
                        for close_btn in close_btns:
                            if close_btn.is_displayed() and close_btn.is_enabled():
                                # Scroll to button if needed
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", close_btn)
                                buffer(0.5)
                                close_btn.click()
                                buffer(1)
                                modal_closed = True
                                break
                    except Exception:
                        continue

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
            if message_modals:
                print_lg("WARNING: Message modal may still be open, forcing additional close attempts")
                # Force close with JavaScript
                driver.execute_script("""
                    var modals = document.querySelectorAll('[class*="msg-overlay"], [class*="artdeco-modal"], [class*="modal-backdrop"]');
                    for (var i = 0; i < modals.length; i++) {
                        modals[i].style.display = 'none';
                    }
                    var closeButtons = document.querySelectorAll('button[aria-label*="Close"], button[class*="dismiss"]');
                    for (var i = 0; i < closeButtons.length; i++) {
                        if (closeButtons[i].offsetParent !== null) {
                            closeButtons[i].click();
                        }
                    }
                """)
                buffer(2)
        except Exception as e:
            print_lg(f"Final modal cleanup warning: {e}")

    except Exception as e:
        print_lg(f"Critical error in modal closing: {e}")


def find_recruiter_on_job_page(driver: WebDriver) -> dict | None:
    '''
    Detects recruiter information from the job posting page.
    Returns a dictionary with recruiter details or None if not found.

    Returns:
    {
        'name': str,
        'title': str,
        'profile_link': str,
        'recruiter_id': str,
        'can_message': bool,
        'is_free_message': bool  # True if free message, False if InMail required
    }
    '''
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
        except NoSuchElementException:
            print_lg("No 'Meet the hiring team' section found on this job posting.")
            return None

        if not hiring_team_section:
            return None

        recruiter_info = {}

        # STEP 2: Find recruiter profile link
        try:
            recruiter_link = hiring_team_section.find_element(By.XPATH, ".//a[contains(@href, '/in/')]")
            recruiter_info['profile_link'] = recruiter_link.get_attribute('href')

            # Extract recruiter ID from profile link
            recruiter_id = recruiter_info['profile_link'].split('/in/')[-1].split('/')[0].split('?')[0]
            recruiter_info['recruiter_id'] = recruiter_id
        except NoSuchElementException:
            return None

        # STEP 3: Find recruiter name
        try:
            name_element = hiring_team_section.find_element(By.XPATH,
                ".//span[contains(@class, 'jobs-poster__name')]")
            recruiter_info['name'] = name_element.text.strip()
        except NoSuchElementException:
            recruiter_info['name'] = "Unknown Recruiter"

        # STEP 4: Find recruiter title
        try:
            title_element = hiring_team_section.find_element(By.XPATH,
                ".//div[contains(@class, 'linked-area')]//div[contains(@class, 'text-body-small')]")
            recruiter_info['title'] = title_element.text.strip()
        except NoSuchElementException:
            recruiter_info['title'] = "Recruiter"

        # STEP 5: Check message capability
        message_capability = check_message_capability(driver, hiring_team_section)
        recruiter_info['can_message'] = message_capability['can_message']
        recruiter_info['is_free_message'] = message_capability['is_free_message']

        print_lg(f"Found recruiter: {recruiter_info['name']} ({recruiter_info['title']}) - "
                f"Can Message: {recruiter_info['can_message']}, Free Message: {recruiter_info['is_free_message']}")

        return recruiter_info

    except Exception as e:
        print_lg(f"Error finding recruiter: {e}")
        return None


def check_message_capability(driver: WebDriver, hiring_team_section: WebElement) -> dict:
    '''
    Checks if recruiter can be messaged and if it's free or requires InMail.

    Returns:
    {
        'can_message': bool,
        'is_free_message': bool,  # True if free, False if InMail
        'message_type': str  # 'free', 'inmail', 'connection', or 'unavailable'
    }
    '''
    result = {
        'can_message': False,
        'is_free_message': False,
        'message_type': 'unavailable'
    }

    try:
        # STEP 1: Find Message button
        try:
            message_button = hiring_team_section.find_element(By.XPATH,
                ".//button[contains(normalize-space(.), 'Message') or contains(@aria-label, 'Message')]")
            result['can_message'] = True
        except NoSuchElementException:
            return result

        # STEP 2: Check connection degree (1st/2nd/3rd)
        try:
            connection_degree = hiring_team_section.find_element(By.XPATH,
                ".//span[contains(@class, 'hirer-card__connection-degree')]")
            degree_text = connection_degree.text.strip()

            if '1st' in degree_text or '2nd' in degree_text:
                result['is_free_message'] = True
                result['message_type'] = 'connection'
                return result
            elif '3rd' in degree_text:
                result['is_free_message'] = False
                result['message_type'] = 'inmail'
                return result
            else:
                result['is_free_message'] = False
                result['message_type'] = 'inmail'
                return result
        except NoSuchElementException:
            # Most LinkedIn recruiters accept free messages, even without visible connection degree
            # Only assume InMail if we have explicit evidence (like InMail button text or premium indicators)
            result['is_free_message'] = True  # Conservative assumption - most recruiters accept free messages
            result['message_type'] = 'free'

        # STEP 3: Check button classes for premium/inmail indicators
        try:
            button_classes = message_button.get_attribute('class')

            if 'premium' in button_classes.lower() or 'inmail' in button_classes.lower():
                result['is_free_message'] = False
                result['message_type'] = 'inmail'
                return result
        except Exception:
            pass

        # STEP 4: Conservative default - assume InMail to prevent unnecessary modal openings
        result['is_free_message'] = False
        result['message_type'] = 'inmail'

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

    Note: This function assumes recruiter_info has been pre-validated to ensure
    messaging is free and available. It should NOT be called for InMail recruiters.
    '''
    global messages_sent_today

    if dry_run_mode:
        print_lg(f"[DRY RUN] Would send message to {recruiter_info['name']}")
        return True, "Dry run - message not actually sent"

    # Ensure no stray modals are open from previous operations
    _ensure_modal_closed(driver)
    buffer(1)  # Extra buffer after modal cleanup

    try:
        # Find and click message button
        message_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(normalize-space(.), 'Message') or contains(@aria-label, 'Message')]"))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", message_button)
        buffer(1)
        message_button.click()
        buffer(2)  # Wait for modal to open

        # Double-check for InMail (safety net - but be more lenient)
        try:
            inmail_elements = driver.find_elements(By.XPATH,
                "//section[contains(@class, 'msg-inmail-credits-display')] | //p[contains(text(), 'InMail credits')] | //span[contains(text(), 'InMail')]")
            if inmail_elements:
                # Check if this is actually blocking the message or just informational
                send_button = driver.find_elements(By.XPATH, "//button[contains(@class, 'msg-form__send-btn')]")
                if send_button and send_button[0].is_enabled():
                    print_lg("InMail elements found but Send button is enabled - proceeding with message")
                else:
                    print_lg("WARNING: InMail detected and Send button disabled - skipping")
                    _ensure_modal_closed(driver)
                    return False, "SKIP: InMail Required (credits detected in modal)"
        except Exception as e:
            print_lg(f"Error checking InMail in modal: {e}")

        # Find and fill message body field (skip subject for regular messages)
        message_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'msg-form__contenteditable') and @contenteditable='true']"))
        )

        # Ensure field is focused and ready
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", message_field)
        driver.execute_script("arguments[0].focus();", message_field)
        buffer(0.5)

        # Clear existing content first
        driver.execute_script("""
            var field = arguments[0];
            field.innerHTML = '';
            field.dispatchEvent(new Event('input', { bubbles: true }));
            field.dispatchEvent(new Event('change', { bubbles: true }));
        """, message_field)
        buffer(0.5)

        # Insert text using a combination of methods for maximum compatibility
        # Method 1: Direct JavaScript insertion with proper event triggering
        driver.execute_script("""
            var field = arguments[0];
            var text = arguments[1];

            // Create a text node and insert it
            var p = document.createElement('p');
            p.appendChild(document.createTextNode(text));
            field.appendChild(p);

            // Trigger multiple events to ensure React detects the change
            field.dispatchEvent(new Event('input', { bubbles: true }));
            field.dispatchEvent(new Event('change', { bubbles: true }));
            field.dispatchEvent(new Event('keydown', { bubbles: true }));
            field.dispatchEvent(new Event('keyup', { bubbles: true }));
            field.dispatchEvent(new Event('keypress', { bubbles: true }));

            // Focus the field
            field.focus();
        """, message_field, message_body)

        buffer(1)  # Allow React to process the input

        # Method 2: Fallback - use Selenium send_keys if JavaScript didn't work
        try:
            entered_text = message_field.get_attribute('innerText').strip()
            if len(entered_text) < 5:
                print_lg("JavaScript insertion failed, trying send_keys fallback")
                message_field.clear()
                message_field.send_keys(message_body)
                buffer(1)
        except Exception as e:
            print_lg(f"Fallback text insertion failed: {e}")

        # Verify text was inserted
        entered_text = message_field.get_attribute('innerText').strip()
        if len(entered_text) < 5:
            return False, f"Text insertion failed - only {len(entered_text)} characters inserted"

        print_lg(f"Successfully inserted {len(entered_text)} characters into message field")

        # Find and click send button with multiple fallback selectors
        send_button = None
        send_selectors = [
            "//button[contains(@class, 'msg-form__send-btn') and not(@disabled)]",
            "//button[contains(@class, 'msg-form__send-btn')]",
            "//button[contains(@aria-label, 'Send') and not(@disabled)]",
            "//button[contains(@aria-label, 'Send message') and not(@disabled)]",
            "//button[contains(text(), 'Send') and not(@disabled)]"
        ]

        for selector in send_selectors:
            try:
                buttons = driver.find_elements(By.XPATH, selector)
                for btn in buttons:
                    if btn.is_displayed() and btn.is_enabled():
                        send_button = btn
                        break
                if send_button:
                    break
            except Exception:
                continue

        if not send_button:
            return False, "Send button not found or disabled"

        # Scroll send button into view and ensure it's clickable
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", send_button)
        buffer(1)

        # Try multiple click methods
        clicked = False
        try:
            # Method 1: Direct click
            send_button.click()
            clicked = True
        except Exception:
            try:
                # Method 2: JavaScript click
                driver.execute_script("arguments[0].click();", send_button)
                clicked = True
            except Exception:
                try:
                    # Method 3: Actions click
                    from selenium.webdriver.common.action_chains import ActionChains
                    ActionChains(driver).move_to_element(send_button).click().perform()
                    clicked = True
                except Exception as e:
                    return False, f"Failed to click send button: {e}"

        if not clicked:
            return False, "Could not click send button with any method"

        buffer(3)  # Wait for send to complete and modal to auto-close

        # Verify message was sent by checking if modal is closed
        buffer(2)  # Give LinkedIn time to process the send
        modal_still_open = False

        try:
            # Check multiple indicators that modal might still be open
            modal_indicators = [
                "//div[contains(@class, 'msg-form__contenteditable')]",
                "//div[contains(@class, 'msg-overlay-modal')]",
                "//div[contains(@class, 'artdeco-modal') and contains(@class, 'msg-form-modal')]",
                "//button[contains(@class, 'msg-form__send-btn')]"
            ]

            for indicator in modal_indicators:
                try:
                    elements = driver.find_elements(By.XPATH, indicator)
                    if elements:
                        modal_still_open = True
                        break
                except Exception:
                    continue

            if modal_still_open:
                print_lg("Message modal still open after send - forcing close")
                _ensure_modal_closed(driver)
                return True, "Message sent successfully (modal force-closed)"
            else:
                print_lg("Message modal auto-closed - send successful")
                return True, ""

        except Exception as e:
            print_lg(f"Error verifying modal closure: {e}")
            # Try to force close anyway to be safe
            _ensure_modal_closed(driver)
            return True, "Message sent successfully (with verification warning)"

        print_lg(f"✅ Message sent successfully to {recruiter_info['name']}")
        messages_sent_today += 1
        messaged_recruiters.add(recruiter_info['recruiter_id'])

        return True, ""

    except Exception as e:
        error_msg = f"Failed to send message: {str(e)}"
        print_lg(error_msg)
        return False, error_msg

    finally:
        # Always ensure modal is closed to prevent stuck state
        buffer(1)  # Give LinkedIn a moment for auto-close
        _ensure_modal_closed(driver)


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
