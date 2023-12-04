# # from modules.open_chrome import *
# from modules.clickers_and_finders import *
# from modules.helpers import *
# from setup.config import *
# from selenium.common.exceptions import NoSuchElementException



# title = "<title>"
# job_id = "<job_id>"

# # Hiring Manager info
# try:
#     # hr_info_card = WebDriverWait(driver,2).until(EC.presence_of_element_located((By.CLASS_NAME, "hirer-card__hirer-information")))
#     # hr_link = hr_info_card.find_element(By.TAG_NAME, "a").get_attribute("href")
#     # hr_name = hr_info_card.find_element(By.TAG_NAME, "span").text
#     # def message_hr(hr_info_card):
#     #     if not hr_info_card: return False
#     #     hr_info_card.find_element(By.XPATH, ".//span[normalize-space()='Message']").click()
#     #     # message_box = driver.find_element(By.XPATH, "//div[@aria-label='Write a message…']")
#     #     # message_box.send_keys()
#     #     if not try_xp(driver, "//button[normalize-space()='Send']"): actions.send_keys(Keys.ESCAPE).perform()
#     #     if max_connections_reached: raise IndexError("Can't connect as Max Connection Request is reached")
#     #     driver.switch_to.new_window('tab')
#     #     driver.get("https://chat.openai.com/")
#     print('Closing browser\'s')
#     # driver.quit()

        
# except Exception as e:
#     print_lg(e)
#     print('Closing browser\'s')
#     from pyautogui import alert
#     alert(e,"Error Occured!")
#     # driver.quit()

import re

def extract_years_of_experience(text):
    # Extract all patterns like '10+ years', '5 years', '3-5 years', etc.
    matches = re.findall(r'(\d+)\s*[-to]*\s*\d*[+]*\s*year[s]?', text, flags=re.IGNORECASE)
    all_years = [int(match) for match in matches]
    return all_years

tests = ["Extract all patterns like '10+ years'\n, '5 years', '3-5 years', 6 - 7 years, 11 to 21 years etc."]

for about in tests:
    print(extract_years_of_experience(about))

