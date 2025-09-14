from random import randint

from fake_useragent import UserAgent
from playwright.sync_api import Browser, BrowserContext, Page, Playwright

from app_settings import AppSettings

"""
Settings to help avoid bot detection by akamai. Change user agent, playwright defaults trigger detection.
"""


def rotate_user_agent() -> str:
    # For testing, other user agent options:
    # ua = UserAgent()  # All user agents
    # ua = UserAgent(min_version=134.0)  # User agents newer than min_version
    # ua = UserAgent(os='Linux')  # User agents from Linux platforms
    ua = UserAgent(os="Mac OS X")  # User agents from Mac platforms
    return ua.random  # returns a random user agent string
    # For testing, return a fixed user agent string
    # return "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"


def setup_context(
    playwright: Playwright, settings: AppSettings
) -> tuple[Browser, BrowserContext]:
    # These were tested on chromium, not sure if they work on other browsers
    # Chromium settings
    browser_args = [
        "--disable-blink-features=AutomationControlled",
        "--ignore-gpu-blocklist",
        "--use-gl=angle",
        "--no-first-run",
        "--enable-automation",
        "--disable-extensions",
        "--disable-infobars",
    ]
    # Other browsers to try
    # browser = playwright.webkit.launch(headless=False, slow_mo=50)
    # browser = playwright.firefox.launch(headless=False, slow_mo=50)
    # browser = playwright.chromium.launch(headless=False, channel='msedge', slow_mo=50)
    browser = playwright.chromium.launch(
        headless=settings.HEADLESS, slow_mo=50, args=browser_args
    )
    context = browser.new_context(
        viewport={"width": 1280, "height": 720}, user_agent=rotate_user_agent()
    )
    return browser, context


def move_mouse(page: Page) -> None:
    randomx = randint(0, 50)
    randomy = randint(0, 50)
    page.mouse.move(randomx, randomy)
    page.mouse.down()
    page.mouse.move(randomx, randomy + 100)
    page.mouse.move(randomx + 100, randomy + 100)
    page.mouse.move(randomx + 100, randomy)
    page.mouse.move(randomx, randomy)
    page.mouse.up()
