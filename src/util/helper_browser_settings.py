from time import sleep
from playwright.sync_api import sync_playwright
from app_settings import AppSettings, log
from utils import move_mouse, setup_context

"""
Test script to verify browser context passes bot detection from bot.sannysoft.com.
Run from the root directory using 'make check_browser' or 'PYTHONPATH=./src python src/util/test_browser_settings.py'

Check this file to validate it's all green
Output: browser_settings.png
"""


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


if __name__ == "__main__":
    test_browser_settings()
