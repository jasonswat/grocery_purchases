import os
import sys
from time import sleep
from playwright.sync_api import sync_playwright

"""
Test script to verify browser context passes bot detection from bot.sannysoft.com.
Run from the root directory `python src/util/test_browser_settings.py` 

Check this file to validate it's all green
Output: browser_settings.png
"""

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")
from app_settings import AppSettings, log
from utils import move_mouse, setup_context


settings = AppSettings()

def test_browser_settings():
    with sync_playwright() as p:
        # Test the browser settings
        browser, context = setup_context(p, settings)
        page = context.new_page()
        page.goto("https://bot.sannysoft.com/")
        page.wait_for_load_state('load')
        move_mouse(page)
        page.screenshot(path='browser_settings.png')
        log.info("Screenshot saved to browser_settings.png, validate all checks are passing.") 
        sleep(10)
        page.close()
        context.close()
        browser.close()

test_browser_settings()