from random import randint
from time import sleep
import logging
from utils import move_mouse, setup_context, setup_logging

def check_credentials():
    username = os.getenv('KROGER_USERNAME')
    password = os.getenv('KROGER_PASSWORD')

    if not username or not password:
        raise EnvironmentError("Environment variables KROGER_USERNAME and KROGER_PASSWORD must be set.")

    return username, password


def sign_in(p, purchases_url, timeout, settings):
    username, password = check_credentials()
    browser, context = setup_context(p, settings)
    page = context.new_page()
    page.goto(purchases_url, timeout=timeout)
    page.wait_for_load_state('load')
    move_mouse(page)
    # Interact with login form, add delays and mouse movement to simulate human behavior
    sleep(randint(3,20))
    page.fill('input#signInName', username)
    sleep(randint(3,20))
    page.fill('input#password', password)
    sleep(randint(3,20))
    move_mouse(page)
    page.click('button#continue:not([disabled]):not([tabindex])')
    user_agent = page.evaluate('() => navigator.userAgent')
    logging.info(f"User-Agent: {user_agent}")
    page.wait_for_url(purchases_url, timeout=timeout)
    return browser, context, page