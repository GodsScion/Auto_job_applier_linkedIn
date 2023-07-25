from modules.open_chrome import *
from modules.clickers_and_finders import *
from modules.helpers import *
from setup.config import *
from selenium.common.exceptions import NoSuchElementException


try: 
    try:
        next_button = wait_span_click(driver, "Next", 1)
        driver.find_element(By.NAME, "file").send_keys(os.path.abspath(resume_file_path))
        next_button = wait_span_click(driver, "Next", 1, False)
        questions_list = []
        while (next_button):
            
            # Find all radio buttons with text as Yes and click them
            yes_radio_buttons = driver.find_elements(By.XPATH, "//label[normalize-space()='Yes']")
            for radio_button in yes_radio_buttons:
                radio_button.click()

            # Find all text inputs and fill them with years_of_experience if it's empty
            text_inputs = driver.find_elements(By.CLASS_NAME, "artdeco-text-input--input")
            for text_input in text_inputs:
                if not text_input.get_attribute("value"): text_input.send_keys(years_of_experience)
            
            # Gathering questions
            all_radio_questions = driver.find_elements(By.CLASS_NAME, "fb-dash-form-element__label")
            for question in all_radio_questions:
                question = question.find_element(By.CLASS_NAME, "visually-hidden").text
                questions_list.append((question, "Yes", "radio"))
            
            all_text_questions = driver.find_elements(By.CLASS_NAME, "artdeco-text-input--label")
            for question in all_text_questions:
                question = question.text
                questions_list.append((question, years_of_experience, "text"))
            
            next_button = driver.find_element(By.XPATH, '//button[contains(span, "Next")]')
            next_button.click()
            buffer(click_gap)

    except NoSuchElementException:
        if questions_list:
            print("Answered the following questions...")
            print(questions_list)
        wait_span_click(driver, "Review", 2)
        wait_span_click(driver, "Submit application", 2)
        print("Successful Test")
except Exception as e:
    print(e)
    actions.send_keys(Keys.ESCAPE).perform()
    driver.find_element(By.XPATH, "//span[normalize-space()='Discard']").click()
    driver.quit()