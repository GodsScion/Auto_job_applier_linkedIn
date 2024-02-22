'''
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

Copyright (C) 2024 Sai Vignesh Golla

License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html
            
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

'''

from modules.open_chrome import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from setup.config import chatGPT_username, chatGPT_password, chatGPT_resume_chat_title, click_gap
from modules.helpers import buffer, manual_login_retry, print_lg
from modules.clickers_and_finders import text_input_by_ID, wait_span_click


# Login Functions
def is_logged_in_GPT():
    if driver.current_url == "https://chat.openai.com/auth/login": return False
    try:
        WebDriverWait(driver,2).until(EC.presence_of_element_located((By.ID, "prompt-textarea")))
        return True
    except Exception as e: 
        print_lg("Didn't find Prompt text area! So highly likely that not logged in!")
        # print_lg(e)
    try:
        driver.find_element(By.XPATH, "//button[contains(., 'Log in')]")
        return False
    except Exception as e:
        print_lg("Didn't find Log In button! Highly likely to be on Human Verification page!")
        # print_lg(e)
    if driver.current_url == "https://chat.openai.com/":
        print_lg("Very high probability we're on Human Verification Page")
        return False
    return False
            
            

def login_GPT():
    # Find the username and password fields and fill them with user credentials
    try:
        gap = click_gap if click_gap > 1 else 2
        if driver.current_url != "https://chat.openai.com/auth/login":
            driver.get("https://chat.openai.com/auth/login")
            buffer(gap)
        wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Log in')]"))).click()
        buffer(gap)
        text_input_by_ID(driver, "username", chatGPT_username)
        buffer(gap)
        driver.find_element(By.XPATH, '//button[@type="submit" and contains(text(), "Continue")]').click()
        buffer(gap)
        text_input_by_ID(driver, "password", chatGPT_password)
        buffer(gap)
        driver.find_element(By.XPATH, '//button[@type="submit" and contains(text(), "Continue") and (not(@aria-hidden) or @aria-hidden!="true")]').click()
        buffer(gap)
    except Exception as e:
        print_lg("Sign in failed! Possibly due to Human Verification. Try logging in manually!")
        # print_lg(e)

    try:
        # Wait until successful redirect, indicating successful login
        wait.until(EC.url_to_be("https://chat.openai.com/"))
        wait.until(EC.presence_of_element_located((By.ID, "prompt-textarea")))
        return print_lg("Login successful!")
    except Exception as e:
        print_lg("Seems like login attempt failed! Possibly due to wrong credentials or already logged in or Human verification! Try logging in manually!")
        # print_lg(e)
        manual_login_retry(is_logged_in_GPT, 2)


def open_resume_chat():
    open_sidebar = wait_span_click(driver, "Open sidebar", 2, False)
    try: open_sidebar = driver.find_element(By.XPATH, '//button[@aria-label="Open sidebar"]')
    except: pass
    if open_sidebar and open_sidebar.is_displayed(): actions.move_to_element(open_sidebar).click().perform()
    driver.find_element(By.LINK_TEXT, chatGPT_resume_chat_title).click()
    close_sidebar = wait_span_click(driver, "Close sidebar", 1, False)
    if close_sidebar and close_sidebar.is_displayed(): actions.move_to_element(close_sidebar).click().perform()

def enter_prompt(prompt):
    text_input_by_ID(driver, "prompt-textarea", prompt, 4.0)
    
def create_custom_resume(job_description):
    pass




def resume_main():
    try:
        driver.get("https://chat.openai.com/")

        # If not logged in, perform the login process
        if not is_logged_in_GPT(): login_GPT()
                
        # Start applying to jobs
        open_resume_chat()
        print_lg("Resume Log In worked")
        
        

    except Exception as e:
        print_lg(e)
        driver.quit()


if __name__ == "__main__": resume_main()
# resume_main()