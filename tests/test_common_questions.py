import os
import sys
import types
import pytest

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
from config.questions import background_check, authorized_to_work


def test_background_check_default():
    result = runAiBot.answer_common_questions('Background CHECK required?', 'No')
    assert result == background_check


def test_authorized_to_work_default():
    text = 'Are you AUTHORIZED to work in this country?'
    result = runAiBot.answer_common_questions(text, 'No')
    assert result == authorized_to_work
