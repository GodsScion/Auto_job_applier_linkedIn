'''
Author:     Antigravity AI
Module:     Universal External Application Form Filler
Purpose:    Automatically detects, fills, and submits job application forms
            on external career portals (Greenhouse, Lever, Workday, Ashby, BambooHR, etc.)
            using candidate configuration and Google Gemini AI.
'''

import os
import re
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from modules.helpers import logger, print_lg


def fill_external_form(driver, resume_path: str, profile: dict, ai_client=None, pause_before_submit: bool = False) -> tuple[bool, str]:
    '''
    Fills an external job application form using applicant profile and Gemini AI.
    Returns (success: bool, status_message: str)
    '''
    try:
        sleep(3)  # Let external page load scripts settle
        current_url = driver.current_url.lower()

        # 1. Detect login walls or Google login / authorization requirements
        page_source_lower = ""
        try: page_source_lower = driver.page_source.lower()
        except Exception: pass

        if any(term in page_source_lower for term in [
            "sign up with google", "continue with google", "sign in with google",
            "sign up now to unlock"
        ]):
            print_lg(f"External job portal requires Google / account login ({current_url}). Skipping per user instructions.")
            return False, "Skipped (Requires Google/Authorisation)"

        if ("login" in current_url or "signin" in current_url) and driver.find_elements(By.CSS_SELECTOR, "input[type='password']"):
            print_lg(f"External job portal requires account login ({current_url}). Saved link for user.")
            return True, "Login Required (Link Saved)"

        # 2. Look for "Apply" / "Apply for this job" button if form is not in view
        apply_triggers = [
            "//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'apply for this job')]",
            "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'apply for this job')]",
            "//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'apply now')]",
            "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'apply now')]",
            "//a[normalize-space()='Apply']",
            "//button[normalize-space()='Apply']",
        ]
        for trigger_xp in apply_triggers:
            try:
                elements = driver.find_elements(By.XPATH, trigger_xp)
                for el in elements:
                    if el.is_displayed() and el.is_enabled():
                        el.click()
                        sleep(2)
                        break
            except Exception:
                pass

        first_name = profile.get("first_name", "")
        last_name = profile.get("last_name", "")
        full_name = f"{first_name} {last_name}".strip()
        email = profile.get("username", "") or profile.get("email", "")
        phone = profile.get("phone_number", "")
        city = profile.get("current_city", "")
        state = profile.get("state", "")
        country = profile.get("country", "")
        zipcode = profile.get("zipcode", "")
        linkedin = profile.get("linkedIn", "")
        website = profile.get("website", "")
        cover_letter = profile.get("cover_letter", "")
        years_exp = profile.get("years_of_experience", "1")
        user_info = profile.get("user_information_all", "")

        # 3. Resume Upload (input[type="file"])
        if resume_path and os.path.exists(resume_path):
            abs_resume = os.path.abspath(resume_path)
            file_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
            for file_in in file_inputs:
                try:
                    file_in.send_keys(abs_resume)
                    print_lg(f"Attached resume ({os.path.basename(abs_resume)}) to external form.")
                    sleep(1)
                    break
                except Exception as e:
                    logger.debug("Resume input not directly attachable: %s", e)

        # 4. Fill text inputs
        inputs = driver.find_elements(By.CSS_SELECTOR, "input:not([type='hidden']):not([type='file']):not([type='submit']):not([type='button']):not([type='checkbox']):not([type='radio'])")
        for inp in inputs:
            try:
                if not inp.is_displayed() or not inp.is_enabled():
                    continue
                current_val = inp.get_attribute("value") or ""
                if current_val.strip():
                    continue  # already filled

                # Identify field by name, id, placeholder, aria-label
                attr_str = " ".join([
                    inp.get_attribute("name") or "",
                    inp.get_attribute("id") or "",
                    inp.get_attribute("placeholder") or "",
                    inp.get_attribute("aria-label") or "",
                    inp.get_attribute("autocomplete") or "",
                ]).lower()

                # Preceding label if available
                label_text = ""
                inp_id = inp.get_attribute("id")
                if inp_id and isinstance(inp_id, str):
                    try:
                        labels = driver.find_elements(By.CSS_SELECTOR, f"label[for='{inp_id}']")
                        if labels and hasattr(labels[0], "text") and isinstance(labels[0].text, str):
                            label_text = labels[0].text.lower()
                    except Exception:
                        pass
                attr_str += " " + label_text

                val_to_type = None
                if any(k in attr_str for k in ["first_name", "firstname", "first name", "given name"]):
                    val_to_type = first_name
                elif any(k in attr_str for k in ["last_name", "lastname", "last name", "surname", "family name"]):
                    val_to_type = last_name
                elif any(k in attr_str for k in ["full_name", "fullname", "full name", "your name", "candidate name"]) or re.search(r'\bname\b', attr_str):
                    val_to_type = full_name
                elif any(k in attr_str for k in ["email", "e-mail"]):
                    val_to_type = email
                elif any(k in attr_str for k in ["phone", "mobile", "telephone", "contact"]):
                    val_to_type = phone
                elif "linkedin" in attr_str:
                    val_to_type = linkedin
                elif any(k in attr_str for k in ["github", "portfolio", "website", "url", "link"]):
                    val_to_type = website
                elif any(k in attr_str for k in ["city", "current city"]):
                    val_to_type = city
                elif any(k in attr_str for k in ["state", "province"]):
                    val_to_type = state
                elif any(k in attr_str for k in ["zip", "postal"]):
                    val_to_type = zipcode
                elif any(k in attr_str for k in ["stipend", "salary", "ctc"]):
                    val_to_type = "15000"
                elif "experience" in attr_str or any(k in attr_str for k in ["how many years", "total experience"]):
                    val_to_type = "1"

                # Fallback to Gemini AI for custom questions
                if val_to_type is None and ai_client and label_text:
                    try:
                        from modules.ai.connections import answer_question
                        ai_ans = answer_question(ai_client, label_text, question_type="text", user_information_all=user_info)
                        if ai_ans and isinstance(ai_ans, str) and ai_ans.strip():
                            val_to_type = ai_ans.strip()
                            print_lg(f'AI answered external input "{label_text}": "{val_to_type}"')
                    except Exception as e:
                        logger.debug("AI answer error on external input: %s", e)

                if val_to_type is None and (inp.get_attribute("required") or "*" in label_text):
                    if inp.get_attribute("type") == "email":
                        val_to_type = email
                    elif inp.get_attribute("type") == "tel":
                        val_to_type = phone
                    elif inp.get_attribute("type") == "number":
                        val_to_type = "1"
                    else:
                        val_to_type = full_name

                if val_to_type:
                    inp.clear()
                    inp.send_keys(val_to_type)
                    sleep(0.2)
            except Exception:
                pass

        # 5. Fill Textareas (Cover letter or custom questions)
        textareas = driver.find_elements(By.TAG_NAME, "textarea")
        for ta in textareas:
            try:
                if not ta.is_displayed() or not ta.is_enabled():
                    continue
                if (ta.get_attribute("value") or "").strip():
                    continue

                attr_str = " ".join([
                    ta.get_attribute("name") or "",
                    ta.get_attribute("id") or "",
                    ta.get_attribute("placeholder") or "",
                    ta.get_attribute("aria-label") or "",
                ]).lower()

                label_text = ""
                ta_id = ta.get_attribute("id")
                if ta_id:
                    labels = driver.find_elements(By.CSS_SELECTOR, f"label[for='{ta_id}']")
                    if labels:
                        label_text = labels[0].text.lower()
                attr_str += " " + label_text

                val = None
                if any(k in attr_str for k in ["cover", "letter", "note", "additional", "message"]):
                    val = cover_letter
                elif ai_client and label_text:
                    try:
                        from modules.ai.connections import answer_question
                        ai_ans = answer_question(ai_client, label_text, question_type="textarea", user_information_all=user_info)
                        if ai_ans and isinstance(ai_ans, str) and ai_ans.strip():
                            val = ai_ans.strip()
                    except Exception as e:
                        logger.debug("AI textarea answer error: %s", e)

                if val:
                    ta.clear()
                    ta.send_keys(val)
                    sleep(0.3)
            except Exception:
                pass

        # 6. Dropdowns (<select>)
        selects = driver.find_elements(By.TAG_NAME, "select")
        for sel_el in selects:
            try:
                if not sel_el.is_displayed():
                    continue
                sel = Select(sel_el)
                opts = [o.text.strip() for o in sel.options if o.text.strip()]
                attr_str = " ".join([
                    sel_el.get_attribute("name") or "",
                    sel_el.get_attribute("id") or "",
                    sel_el.get_attribute("aria-label") or "",
                ]).lower()

                # Work auth
                if any(k in attr_str for k in ["authorized", "legally", "eligibility"]):
                    for opt in opts:
                        if opt.lower() in ["yes", "authorized", "i am authorized"]:
                            sel.select_by_visible_text(opt)
                            break
                # Sponsorship
                elif any(k in attr_str for k in ["sponsor", "visa"]):
                    for opt in opts:
                        if opt.lower() in ["no", "will not require", "do not require"]:
                            sel.select_by_visible_text(opt)
                            break
                # Country
                elif "country" in attr_str:
                    for opt in opts:
                        if country.lower() in opt.lower():
                            sel.select_by_visible_text(opt)
                            break
                # Gender
                elif "gender" in attr_str:
                    gender = profile.get("gender", "")
                    if gender:
                        for opt in opts:
                            if gender.lower() in opt.lower():
                                sel.select_by_visible_text(opt)
                                break
                elif ai_client and opts:
                    try:
                        from modules.ai.connections import answer_question
                        ai_choice = answer_question(ai_client, attr_str, question_type="single_select", options=opts, user_information_all=user_info)
                        if ai_choice:
                            for opt in opts:
                                if ai_choice.lower() in opt.lower() or opt.lower() in ai_choice.lower():
                                    sel.select_by_visible_text(opt)
                                    break
                    except Exception:
                        pass
            except Exception:
                pass

        # 7. Checkboxes (Consent / Terms / Privacy)
        checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
        for cb in checkboxes:
            try:
                if not cb.is_displayed() or cb.is_selected():
                    continue
                attr_str = " ".join([
                    cb.get_attribute("name") or "",
                    cb.get_attribute("id") or "",
                    cb.get_attribute("aria-label") or "",
                ]).lower()
                cb_id = cb.get_attribute("id")
                label_text = ""
                if cb_id:
                    labels = driver.find_elements(By.CSS_SELECTOR, f"label[for='{cb_id}']")
                    if labels:
                        label_text = labels[0].text.lower()
                combined = attr_str + " " + label_text
                if any(w in combined for w in ["agree", "consent", "privacy", "terms", "policy", "acknowledge", "certify"]) or cb.get_attribute("required"):
                    try:
                        cb.click()
                    except Exception:
                        driver.execute_script("arguments[0].click();", cb)
                    sleep(0.2)
            except Exception:
                pass

        # 8. Submit Application or Pause
        submit_xpaths = [
            "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit application')]",
            "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit')]",
            "//input[@type='submit']",
            "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'apply now')]",
        ]

        if pause_before_submit:
            print_lg("External job form completed! (Paused before submission per user configuration)")
            sleep(4)
            return True, "External Form Filled (Paused before submit)"

        for s_xp in submit_xpaths:
            try:
                sub_btns = driver.find_elements(By.XPATH, s_xp)
                for btn in sub_btns:
                    if btn.is_displayed() and btn.is_enabled():
                        btn.click()
                        print_lg("Clicked external Submit Application button!")
                        sleep(3)
                        return True, "External Applied"
            except Exception:
                pass

        return True, "External Form Filled"

    except Exception as e:
        logger.warning("External form filler exception: %s", e)
        return False, f"Failed: {e}"
