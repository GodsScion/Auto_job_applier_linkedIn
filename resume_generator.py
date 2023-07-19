from openChrome import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import chatGPT_username, chatGPT_password, chatGPT_resume_chat_title, click_gap
from helpers import buffer, manual_login_retry
from clickers_and_finders import text_input_by_ID, wait_span_click


# Login Functions
def is_logged_in_GPT():
    if wait_span_click(driver, "Verify you are human", 3): return False
    if driver.current_url == "https://chat.openai.com/": return True
    if driver.current_url == "https://chat.openai.com/auth/login": return False
    try:
        driver.find_element(By.XPATH, "//button[contains(., 'Log in')]")
        return False
    except Exception as e1:
        try:
            driver.find_element(By.ID, "prompt-textarea")
            return True
        except Exception as e2:
            # print(e1, e2)
            print("Didn't find Prompt text area, so assuming user is not logged in!")
            

def login_GPT():
    # Find the username and password fields and fill them with user credentials
    try:
        gap = click_gap if click_gap > 1 else 2
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
        print("Sign in failed! Possibly due to Human Verification. Try logging in manually!")
        # print(e)

    try:
        # Wait until successful redirect, indicating successful login
        wait.until(EC.url_to_be("https://chat.openai.com/"))
        wait.until(EC.presence_of_element_located((By.ID, "prompt-textarea")))
        return print("Login successful!")
    except Exception as e:
        print("Seems like login attempt failed! Possibly due to wrong credentials or already logged in or Human verification! Try logging in manually!")
        # print(e)
        manual_login_retry(is_logged_in_GPT)


def open_resume_chat():
    wait_span_click(driver, "Open sidebar", 2, False)
    try:
        driver.find_element(By.LINK_TEXT, chatGPT_resume_chat_title).click()
    except:
        print()

def enter_prompt(prompt):
    text_input_by_ID(driver, "prompt-textarea", prompt, 4.0)
    



def resume_main():
    from openChrome import driver, wait, actions
    try:
        driver.get("https://chat.openai.com/")

        # If not logged in, perform the login process
        if not is_logged_in_GPT(): login_GPT()
                
        # Start applying to jobs
        open_resume_chat()
        print("Log In worked")
        
        

    except Exception as e:
        print(e)
        driver.quit()

if __name__ == "__main__":
    resume_main()