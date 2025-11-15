import os
from random import randint
from time import sleep
from app_settings import get_log
from utils import move_mouse, setup_context
from bs4 import BeautifulSoup, Tag
from urllib.parse import urlparse

log = get_log()


def random_sleep(max_sleep):
    sleep_time = randint(3, max_sleep)
    log.info(f"Sleeping for {sleep_time} seconds to simulate human interaction.")
    sleep(sleep_time)


def get_basename_from_url(url):
    parsed_url = urlparse(url)
    return os.path.basename(parsed_url.path)


def ensure_signed_in(page, settings, success_url):
    """Checks if we are on the login page, and if so, signs in."""
    if page.is_visible("input#signInName"):
        log.info("Login page detected. Signing in.")
        username = settings.KROGER_USERNAME
        password = settings.KROGER_PASSWORD.get_secret_value()
        max_sleep = settings.MAX_SLEEP
        timeout = settings.TIMEOUT

        move_mouse(page)
        random_sleep(max_sleep)
        page.fill("input#signInName", username)
        random_sleep(max_sleep)
        page.fill("input#password", password)
        random_sleep(max_sleep)
        move_mouse(page)
        page.click("button#continue:not([disabled]):not([tabindex])")
        page.wait_for_url(success_url, timeout=timeout)
        log.info("Sign-in successful.")
    else:
        log.info("Already signed in or not on the login page.")


def get_receipts(page, purchases_url, redirect_url, settings):
    max_sleep = settings.MAX_SLEEP
    page.goto(purchases_url)
    ensure_signed_in(page, settings, purchases_url)
    random_sleep(max_sleep)
    page.wait_for_load_state("load")
    page.is_visible("div.PurchaseResultsColumn")
    page.goto(redirect_url)
    ensure_signed_in(page, settings, redirect_url)
    random_sleep(max_sleep)
    page.wait_for_load_state("load")
    page.is_visible("div.PurchaseResultsColumn")
    html = page.inner_html("#PurchaseResultsColumn")
    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all(
        "a",
        {
            "class": "kds-Link kds-Link--inherit kds-Link--implied block p-16 text-neutral-most-prominent no-underline sm:py-24"
        },
    )
    # log.debug(f"Links: {links}")
    receipts = []
    for a in links:
        # log.debug(f"a: {a}")
        if isinstance(a, Tag):
            href = a.get("href")
            if href:
                receipt_id = get_basename_from_url(href)
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
    page.wait_for_load_state("load")
    move_mouse(page)
    # Interact with login form, add delays and mouse movement to simulate human behavior
    random_sleep(max_sleep)
    page.fill("input#signInName", username)
    random_sleep(max_sleep)
    page.fill("input#password", password)
    random_sleep(max_sleep)
    move_mouse(page)
    page.click("button#continue:not([disabled]):not([tabindex])")
    user_agent = page.evaluate("() => navigator.userAgent")
    log.info(f"User-Agent: {user_agent}")
    page.wait_for_url(purchases_url, timeout=timeout)
    return browser, context, page


def get_receipt_html(page, receipt_url, settings):
    timeout = settings.TIMEOUT
    max_sleep = settings.MAX_SLEEP
    page.goto(receipt_url, timeout=timeout)
    ensure_signed_in(page, settings, receipt_url)
    random_sleep(max_sleep)
    page.wait_for_load_state("load")
    page.is_visible("div.Receipt-container")
    html = page.inner_html("div.Receipt-container")
    return html
