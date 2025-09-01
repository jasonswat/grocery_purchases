import os
from random import randint
from time import sleep
from app_settings import log
from utils import move_mouse, setup_context
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def random_sleep(max_sleep):
    sleep_time = randint(3, max_sleep)
    log.info(f"Sleeping for {sleep_time} seconds to simulate human interaction.")
    sleep(sleep_time)

def get_basename_from_url(url):
    parsed_url = urlparse(url)
    return os.path.basename(parsed_url.path)

def get_receipts(page, purchases_url, redirect_url, settings):
    max_sleep = settings.MAX_SLEEP
    page.goto(purchases_url)
    random_sleep(max_sleep)
    page.wait_for_load_state('load')
    page.is_visible('div.PurchaseResultsColumn')
    page.goto(redirect_url)
    random_sleep(max_sleep)
    page.wait_for_load_state('load')
    page.is_visible('div.PurchaseResultsColumn')
    html = page.inner_html('#PurchaseResultsColumn')
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a', {'class': 'kds-Link kds-Link--inherit kds-Link--implied block p-16 text-neutral-most-prominent no-underline sm:py-24'})
    log.debug(f"Links: {links}")
    receipts = []
    for a in links:
        log.debug(f"a: {a}")
        receipt_id = get_basename_from_url(a['href'])
        receipts.append(receipt_id)
        log.debug(f"receipt_id: {receipt_id}")
    log.info(f"Found {len(receipts)} receipts {receipts}.")
    return receipts

def sign_in(p, purchases_url, settings):
    username = settings.KROGER_USERNAME
    password = settings.KROGER_PASSWORD.get_secret_value()
    timeout = settings.TIMEOUT
    max_sleep = settings.MAX_SLEEP
    browser, context = setup_context(p, settings)
    page = context.new_page()
    page.goto(purchases_url, timeout=timeout)
    page.wait_for_load_state('load')
    move_mouse(page)
    # Interact with login form, add delays and mouse movement to simulate human behavior
    random_sleep(max_sleep)
    page.fill('input#signInName', username)
    random_sleep(max_sleep)
    page.fill('input#password', password)
    random_sleep(max_sleep)
    move_mouse(page)
    page.click('button#continue:not([disabled]):not([tabindex])')
    user_agent = page.evaluate('() => navigator.userAgent')
    log.info(f"User-Agent: {user_agent}")
    page.wait_for_url(purchases_url, timeout=timeout)
    return browser, context, page