'''
Unit tests for build_search_url and Universal External Form Filler
'''

import sys
import types
import pytest
from unittest.mock import MagicMock, patch

# Stub open_chrome so importing runAiBot does not launch Chrome
fake_chrome = types.ModuleType("modules.open_chrome")
fake_chrome.options = fake_chrome.driver = fake_chrome.actions = fake_chrome.wait = None
sys.modules["modules.open_chrome"] = fake_chrome

from modules.external_form_filler import fill_external_form
from runAiBot import build_search_url


def test_build_search_url_encodes_internship_and_location():
    url = build_search_url("Software Engineer Intern")
    assert "keywords=Software+Engineer+Intern" in url or "keywords=Software%20Engineer%20Intern" in url
    # 1 is Internship in f_E
    assert "f_E=" in url
    assert "1" in url
    # location should be present
    assert "location=" in url


def test_external_form_filler_handles_login_wall():
    mock_driver = MagicMock()
    mock_driver.current_url = "https://example.myworkdayjobs.com/en-US/careers/login"
    mock_driver.find_elements.return_value = [MagicMock()]  # password input present

    success, status = fill_external_form(
        mock_driver,
        resume_path="",
        profile={},
        ai_client=None
    )
    assert success is True
    assert "Login Required" in status


def test_external_form_filler_fills_basic_fields():
    mock_driver = MagicMock()
    mock_driver.current_url = "https://boards.greenhouse.io/job/12345"
    
    # Mock inputs
    mock_first_name = MagicMock()
    mock_first_name.is_displayed.return_value = True
    mock_first_name.is_enabled.return_value = True
    mock_first_name.get_attribute.side_effect = lambda attr: "first_name" if attr == "name" else ""

    mock_email = MagicMock()
    mock_email.is_displayed.return_value = True
    mock_email.is_enabled.return_value = True
    mock_email.get_attribute.side_effect = lambda attr: "email" if attr == "name" else ""

    # Mock submit button
    mock_submit = MagicMock()
    mock_submit.is_displayed.return_value = True
    mock_submit.is_enabled.return_value = True
    mock_submit.text = "Submit Application"

    def mock_find_elements(by, value):
        if "input:not" in value:
            return [mock_first_name, mock_email]
        elif "submit application" in value.lower():
            return [mock_submit]
        return []

    mock_driver.find_elements.side_effect = mock_find_elements

    profile = {
        "first_name": "Reyaz",
        "last_name": "Ali",
        "username": "reyaz@example.com",
        "phone_number": "1234567890",
    }

    success, status = fill_external_form(
        mock_driver,
        resume_path="",
        profile=profile,
        ai_client=None,
        pause_before_submit=False
    )
    assert success is True
    assert "Applied" in status or "Filled" in status
    mock_first_name.send_keys.assert_called_with("Reyaz")
    mock_email.send_keys.assert_called_with("reyaz@example.com")
