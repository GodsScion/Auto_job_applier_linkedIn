from config import click_gap
from helpers import buffer
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# Click Functions
def wait_span_click(driver, x, time=5.0, click=True):
    if x:
        try:
            button = WebDriverWait(driver,time).until(EC.presence_of_element_located((By.XPATH, '//span[normalize-space(.)="'+x+'"]')))
            scroll_to_view(driver, button)
            if click:
                button.click()
                buffer(click_gap)
            return button
        except Exception as e:
            print("Click Failed! Didn't find '"+x+"'")
            # print(e)
            return False

def multi_sel(driver, l, time=5.0):
    for x in l:
        try:
            button = WebDriverWait(driver,time).until(EC.presence_of_element_located((By.XPATH, '//span[normalize-space(.)="'+x+'"]')))
            scroll_to_view(driver, button)
            button.click()
            buffer(click_gap)
        except Exception as e:
            print("Click Failed! Didn't find '"+x+"'")
            # print(e)

def multi_sel_noWait(driver, l):
    for x in l:
        try:
            button = driver.find_element(By.XPATH, '//span[normalize-space(.)="'+x+'"]')
            scroll_to_view(driver, button)
            button.click()
            buffer(click_gap)
        except Exception as e:
            print("Click Failed! Didn't find '"+x+"'")
            # print(e)

def boolean_button_click(driver, actions, x):
    try:
        list_container = driver.find_element(By.XPATH, '//h3[normalize-space()="'+x+'"]/ancestor::fieldset')
        button = list_container.find_element(By.XPATH, './/input[@role="switch"]')
        scroll_to_view(driver, button)
        actions.move_to_element(button).click().perform()
        buffer(click_gap)
    except Exception as e:
        print("Click Failed! Didn't find '"+x+"'")
        # print(e)

# Find functions
def find_by_class(driver, class_name, time=5.0):
    return WebDriverWait(driver, time).until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))

# Scroll functions
def scroll_to_view(driver, element):
    return driver.execute_script("arguments[0].scrollIntoView(true);", element)

# Enter input text functions
def text_input_by_ID(driver, id, value, time=5.0):
    username_field = WebDriverWait(driver, time).until(EC.presence_of_element_located((By.ID, id)))
    username_field.send_keys(Keys.CONTROL + "a")
    return username_field.send_keys(value)