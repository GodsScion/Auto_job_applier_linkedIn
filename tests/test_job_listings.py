import os
import sys
import types
import tempfile
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
mock_pg = types.ModuleType('pyautogui')
mock_pg.FAILSAFE = False
mock_pg.alert = lambda *a, **k: None
mock_pg.confirm = lambda *a, **k: None
sys.modules['pyautogui'] = mock_pg
stub = types.ModuleType('modules.open_chrome')
stub.driver = None
stub.wait = None
sys.modules['modules.open_chrome'] = stub
import importlib
runAiBot = importlib.import_module('runAiBot')

HTML = """
<html><body>
<div class='scaffold-layout__list'>
<ul>
<li class='scaffold-layout__list-item' data-occludable-job-id='1'><a href='#'>Job 1</a></li>
<li class='scaffold-layout__list-item' data-occludable-job-id='2'><a href='#'>Job 2</a></li>
</ul>
</div>
</body></html>
"""

HTML_NO_ATTR = """
<html><body>
<div class='scaffold-layout__list'>
<ul>
<li class='scaffold-layout__list-item'><a href='#'>Job 1</a></li>
<li class='scaffold-layout__list-item'><a href='#'>Job 2</a></li>
</ul>
</div>
</body></html>
"""

def start_driver():
    options = Options()
    options.add_argument('--headless=new')
    try:
        driver = webdriver.Chrome(options=options)
    except Exception:
        pytest.skip('WebDriver not available in test environment')
    return driver


def test_find_job_listings(tmp_path):
    html_file = tmp_path / 'page.html'
    html_file.write_text(HTML)
    driver = start_driver()
    try:
        runAiBot.driver = driver
        runAiBot.wait = WebDriverWait(driver, 1)
        driver.get(html_file.as_uri())
        items = runAiBot.find_job_listings()
        assert len(items) == 2
    finally:
        driver.quit()


def test_find_job_listings_fallback(tmp_path):
    html_file = tmp_path / 'page.html'
    html_file.write_text(HTML_NO_ATTR)
    driver = start_driver()
    try:
        runAiBot.driver = driver
        runAiBot.wait = WebDriverWait(driver, 1)
        driver.get(html_file.as_uri())
        items = runAiBot.find_job_listings()
        assert len(items) == 2
    finally:
        driver.quit()
