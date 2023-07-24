from modules.open_chrome import *
from modules.clickers_and_finders import *
from modules.helpers import *



try: 
    # parent_div = find_by_class(driver, "jobs-unified-top-card__primary-description")
    time_posted_text = driver.find_element(By.XPATH, '//span[contains(normalize-space(), "ago")]').text
    if time_posted_text.__contains__("Reposted"):
        repost = True
        time_posted_text = time_posted_text.replace("Reposted", "")
    date_listed = calculate_date_posted(time_posted_text)
    print(date_listed)
except Exception as e:
    print(e)
    driver.quit()