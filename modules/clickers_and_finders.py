'''
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

Copyright (C) 2024 Sai Vignesh Golla

License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html
            
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

'''

from setup.config import click_gap, smooth_scroll
from modules.helpers import buffer, print_lg
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# Click Functions
def wait_span_click(driver, x, time=5.0, click=True, scroll=True, scrollTop = False):
    if x:
        try:
            button = WebDriverWait(driver,time).until(EC.presence_of_element_located((By.XPATH, '//span[normalize-space(.)="'+x+'"]')))
            if scroll:  scroll_to_view(driver, button, scrollTop)
            if click:
                button.click()
                buffer(click_gap)
            return button
        except Exception as e:
            print_lg("Click Failed! Didn't find '"+x+"'")
            # print_lg(e)
            return False

def multi_sel(driver, l, time=5.0):
    for x in l:
        try:
            button = WebDriverWait(driver,time).until(EC.presence_of_element_located((By.XPATH, '//span[normalize-space(.)="'+x+'"]')))
            scroll_to_view(driver, button)
            button.click()
            buffer(click_gap)
        except Exception as e:
            print_lg("Click Failed! Didn't find '"+x+"'")
            # print_lg(e)

def multi_sel_noWait(driver, l, actions=False):
    for x in l:
        try:
            button = driver.find_element(By.XPATH, '//span[normalize-space(.)="'+x+'"]')
            scroll_to_view(driver, button)
            button.click()
            buffer(click_gap)
        except Exception as e:
            if actions: company_search_click(driver,actions,x)
            else:   print_lg("Click Failed! Didn't find '"+x+"'")
            # print_lg(e)

def boolean_button_click(driver, actions, x):
    try:
        list_container = driver.find_element(By.XPATH, '//h3[normalize-space()="'+x+'"]/ancestor::fieldset')
        button = list_container.find_element(By.XPATH, './/input[@role="switch"]')
        scroll_to_view(driver, button)
        actions.move_to_element(button).click().perform()
        buffer(click_gap)
    except Exception as e:
        print_lg("Click Failed! Didn't find '"+x+"'")
        # print_lg(e)

# Find functions
def find_by_class(driver, class_name, time=5.0):
    return WebDriverWait(driver, time).until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))

# Scroll functions
def scroll_to_view(driver, element, top = False, smooth_scroll = smooth_scroll):
    if top: return driver.execute_script('arguments[0].scrollIntoView();', element)
    behavior = "smooth" if smooth_scroll else "instant"
    return driver.execute_script('arguments[0].scrollIntoView({block: "center", behavior: "'+behavior+'" });', element)

# Enter input text functions
def text_input_by_ID(driver, id, value, time=5.0):
    username_field = WebDriverWait(driver, time).until(EC.presence_of_element_located((By.ID, id)))
    username_field.send_keys(Keys.CONTROL + "a")
    return username_field.send_keys(value)

def try_xp(driver, xpath, click=True):
    try: 
        if click:
            driver.find_element(By.XPATH, xpath).click()
            return True
        else:
            return driver.find_element(By.XPATH, xpath)
    except: return False

def try_linkText(driver, linkText):
    try:    return driver.find_element(By.LINK_TEXT, linkText)
    except:  return False

def try_find_by_classes(driver, classes):
    for cla in classes:
        try:    return driver.find_element(By.CLASS_NAME, cla)
        except: pass
    raise Exception("Failed to find an element with given classes")

def company_search_click(driver,actions,x):
    wait_span_click(driver,"Add a company",1)
    search = driver.find_element(By.XPATH,"(//input[@placeholder='Add a company'])[1]")
    search.send_keys(Keys.CONTROL + "a")
    search.send_keys(x)
    buffer(3)
    actions.send_keys(Keys.DOWN).perform()
    actions.send_keys(Keys.ENTER).perform()
    print_lg(f'Tried searching and adding "{x}"')