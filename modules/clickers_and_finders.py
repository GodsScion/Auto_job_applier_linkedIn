'''
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

Copyright (c) 2024-2026 Sai Vignesh Golla

License:    MIT License
            https://opensource.org/license/mit
            
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

Support me: https://github.com/sponsors/GodsScion
'''

from config.settings import click_gap, smooth_scroll
from modules.helpers import buffer, human_type, logger, print_lg, sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException


# Matching helpers
def text_xpath(tag: str, text: str) -> str:
    '''
    XPath matching a `tag` whose text contains `text`, ignoring case and surrounding
    whitespace. LinkedIn re-words and re-cases its labels, exact matches keep breaking.
    '''
    # ponytail: translate() lowercases ASCII only, English labels are all this project targets.
    return (f'.//{tag}[contains(translate(normalize-space(.), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", '
            f'"abcdefghijklmnopqrstuvwxyz"), "{text.strip().lower()}")]')

def pick_first_displayed(elements: list[WebElement]) -> WebElement | None:
    '''
    Returns the first visible element of `elements`, or `None` if none are visible.
    LinkedIn renders hidden 0x0 duplicates that `find_element` happily returns first,
    and clicking those is what silently fails.
    '''
    for element in elements:
        try:
            if element.is_displayed(): return element
        except StaleElementReferenceException:
            continue
    return None

def wait_for_displayed(driver: WebDriver, xpath: str, time: float) -> WebElement:
    '''Waits up to `time` seconds for a *visible* element matching `xpath`, else raises `TimeoutException`.'''
    return WebDriverWait(driver, time).until(lambda d: pick_first_displayed(d.find_elements(By.XPATH, xpath)))

# Click Functions
def wait_span_click(driver: WebDriver, text: str, time: float=5.0, click: bool=True, scroll: bool=True, scrollTop: bool=False) -> WebElement | bool:
    '''
    Finds the span element with the given `text`.
    - Returns `WebElement` if found, else `False` if not found.
    - Clicks on it if `click = True`.
    - Will spend a max of `time` seconds in searching for each element.
    - Will scroll to the element if `scroll = True`.
    - Will scroll to the top if `scrollTop = True`.
    '''
    if text:
        try:
            button = wait_for_displayed(driver, text_xpath("span", text), time)
            if scroll:  scroll_to_view(driver, button, scrollTop)
            if click:
                button.click()
                buffer(click_gap)
            return button
        except Exception as e:
            logger.warning("Click Failed! Didn't find '%s' (%s)", text, type(e).__name__)
            return False

def wait_xp_click(driver: WebDriver | WebElement, xpath: str, time: float=5.0, scrollTop: bool=False) -> WebElement | bool:
    '''
    Same contract as `wait_span_click`, but takes an `xpath` instead of a span's text, so
    callers can anchor on an `id` or `aria-label` and scope the search to a modal.
    - Returns the clicked `WebElement`, or `False` if nothing visible matched.
    '''
    try:
        button = wait_for_displayed(driver, xpath, time)
        scroll_to_view(driver, button, scrollTop)
        button.click()
        buffer(click_gap)
        return button
    except Exception as e:
        logger.warning('Click Failed! Nothing visible matching "%s" (%s)', xpath, type(e).__name__)
        return False

def multi_sel_noWait(driver: WebDriver, texts: list, actions: ActionChains = None) -> None:
    '''
    - For each text in the `texts`, tries to find and click `span` element with that class.
    - If `actions` is provided, bot tries to search and Add the `text` to this filters list section.
    - Won't wait to search for each element, assumes that element is rendered.
    '''
    for text in texts:
        try:
            button = pick_first_displayed(driver.find_elements(By.XPATH, text_xpath("span", text)))
            if not button: raise NoSuchElementException(f'No visible span matching "{text}"')
            scroll_to_view(driver, button)
            button.click()
            buffer(click_gap)
        except Exception as e:
            if actions: company_search_click(driver,actions,text)
            else:   logger.warning("Click Failed! Didn't find '%s' (%s)", text, type(e).__name__)

def boolean_button_click(driver: WebDriver, actions: ActionChains, text: str) -> None:
    '''
    Tries to click on the boolean button with the given `text` text.
    '''
    try:
        list_container = driver.find_element(By.XPATH, text_xpath("h3", text) + '/ancestor::fieldset')
        # The switch input itself is often visually hidden by design, so don't filter it on displayed.
        button = list_container.find_element(By.XPATH, './/input[@role="switch"]')
        scroll_to_view(driver, button)
        actions.move_to_element(button).click().perform()
        buffer(click_gap)
    except Exception as e:
        logger.warning("Click Failed! Didn't find '%s' (%s)", text, type(e).__name__)

# Find functions
def find_by_class(driver: WebDriver, class_name: str, time: float=5.0) -> WebElement | Exception:
    '''
    Waits for a max of `time` seconds for element to be found, and returns `WebElement` if found, else `Exception` if not found.
    '''
    return WebDriverWait(driver, time).until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))

# Scroll functions
def scroll_to_view(driver: WebDriver, element: WebElement, top: bool = False, smooth_scroll: bool = smooth_scroll) -> None:
    '''
    Scrolls the `element` to view.
    - `smooth_scroll` will scroll with smooth behavior.
    - `top` will scroll to the `element` to top of the view.
    '''
    # Callers scope searches to a modal and pass that WebElement in here as `driver`.
    # Only the WebDriver can run scripts; every element knows its own driver as `.parent`.
    if not hasattr(driver, "execute_script"): driver = element.parent
    if top:
        return driver.execute_script('arguments[0].scrollIntoView();', element)
    behavior = "smooth" if smooth_scroll else "instant"
    return driver.execute_script('arguments[0].scrollIntoView({block: "center", behavior: "'+behavior+'" });', element)

def try_xp(driver: WebDriver, xpath: str, click: bool=True) -> WebElement | bool:
    try:
        if click:
            driver.find_element(By.XPATH, xpath).click()
            buffer(click_gap)
            return True
        else:
            return driver.find_element(By.XPATH, xpath)
    except NoSuchElementException: return False     # simply not on the page, nothing to report
    except Exception as e:
        logger.warning('Failed to %s element with xpath "%s"! %s', "click" if click else "find", xpath, e)
        return False

def try_linkText(driver: WebDriver, linkText: str) -> WebElement | bool:
    try:    return driver.find_element(By.LINK_TEXT, linkText)
    except NoSuchElementException:  return False
    except Exception as e:
        logger.warning('Failed to find link "%s"! %s', linkText, e)
        return False

def try_find_by_classes(driver: WebDriver, classes: list[str]) -> WebElement | ValueError:
    for cla in classes:
        try:    return driver.find_element(By.CLASS_NAME, cla)
        except NoSuchElementException: pass
        except Exception as e:  logger.warning('Failed to find element with class "%s"! %s', cla, e)
    raise ValueError("Failed to find an element with given classes")

def company_search_click(driver: WebDriver, actions: ActionChains, companyName: str) -> None:
    '''
    Tries to search and Add the company to company filters list.
    '''
    wait_span_click(driver,"Add a company",1)
    search = driver.find_element(By.XPATH,"(.//input[@placeholder='Add a company'])[1]")
    search.send_keys(Keys.CONTROL + "a")
    human_type(search, companyName)
    buffer(3)
    actions.send_keys(Keys.DOWN).perform()
    actions.send_keys(Keys.ENTER).perform()
    print_lg(f'Tried searching and adding "{companyName}"')

def text_input(actions: ActionChains, textInputEle: WebElement | bool, value: str, textFieldName: str = "Text") -> None | Exception:
    if textInputEle:
        sleep(1)
        # actions.key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).perform()
        textInputEle.clear()
        human_type(textInputEle, value.strip())
        sleep(2)
        actions.send_keys(Keys.ENTER).perform()
    else:
        logger.warning('%s input was not given!', textFieldName)