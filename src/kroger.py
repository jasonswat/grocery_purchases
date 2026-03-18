import os
from random import randint
from time import sleep
from app_settings import get_log
from utils import move_mouse, setup_context
from bs4 import BeautifulSoup, Tag
from urllib.parse import urlparse
from playwright.sync_api import TimeoutError

log = get_log()


def random_sleep(max_sleep):
    sleep_time = randint(3, max_sleep)
    log.debug(f"Sleeping for {sleep_time} seconds to simulate human interaction.")
    sleep(sleep_time)


def get_basename_from_url(url):
    parsed_url = urlparse(url)
    return os.path.basename(parsed_url.path)


def _perform_login(page, settings, success_url):
    """Fills out and submits the login form."""
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


def ensure_signed_in(page, settings, purchases_url):
    """Checks if we are on the login page, and if so, signs in."""
    try:
        page.wait_for_selector("input#signInName", state="visible", timeout=5000)
        log.info("Login page detected. Signing in.")
        _perform_login(page, settings, purchases_url)
    except TimeoutError:
        log.info("Already signed in or not on the login page.")


def get_receipts(page, purchases_url, redirect_url, settings):
    max_sleep = settings.MAX_SLEEP
    timeout = settings.TIMEOUT
    log.debug(f"Navigating to purchases url: {purchases_url}")
    page.goto(purchases_url)
    ensure_signed_in(page, settings, purchases_url)
    random_sleep(max_sleep)
    page.wait_for_load_state("load")
    log.debug("Waiting for purchase results column.")
    page.wait_for_selector("#PurchaseResultsColumn", timeout=timeout)
    log.debug("Purchase results column found.")

    log.debug(f"Navigating to redirect url: {redirect_url}")
    page.goto(redirect_url)
    ensure_signed_in(page, settings, redirect_url)
    random_sleep(max_sleep)
    page.wait_for_load_state("load")
    log.debug("Waiting for purchase results column on redirect page.")
    page.wait_for_selector("#PurchaseResultsColumn", timeout=timeout)
    log.debug("Purchase results column found on redirect page.")
    log.debug("Getting inner html of #PurchaseResultsColumn")
    html = page.inner_html("#PurchaseResultsColumn")
    log.debug(f"HTML received (first 500 chars): {html[:500]}")
    soup = BeautifulSoup(html, "html.parser")
    # We find list items for purchases and then find the link within them.
    purchase_list_items = soup.find_all("li", {"class": "PO-NonPendingPurchase"})
    log.debug(f"Found {len(purchase_list_items)} purchase list items.")
    links = []
    for item in purchase_list_items:
        link = item.find("a")
        if link:
            links.append(link)

    log.debug(f"Found {len(links)} links.")
    log.debug(f"Links: {links}")
    receipts = []
    for a in links:
        log.debug(f"a: {a}")
        if isinstance(a, Tag):
            href = a.get("href")
            if href:
                receipt_id = get_basename_from_url(href)
                receipts.append(receipt_id)
                log.debug(f"receipt_id: {receipt_id}")
    log.info(f"Found {len(receipts)} receipts {receipts}.")
    return receipts


def sign_in(p, purchases_url, settings):
    timeout = settings.TIMEOUT
    browser, context = setup_context(p, settings)
    page = context.new_page()
    page.goto(purchases_url, timeout=timeout)
    page.wait_for_load_state("load")
    move_mouse(page)
    # Interact with login form, add delays and mouse movement to simulate human behavior
    _perform_login(page, settings, purchases_url)
    user_agent = page.evaluate("() => navigator.userAgent")
    log.info(f"User-Agent: {user_agent}")
    return browser, context, page


def get_receipt_html(page, receipt_url, settings):
    timeout = settings.TIMEOUT
    max_sleep = settings.MAX_SLEEP
    page.goto(receipt_url, timeout=timeout)
    ensure_signed_in(page, settings, receipt_url)
    random_sleep(max_sleep)
    page.wait_for_load_state("load")
    page.wait_for_selector("div.Receipt-container")
    html = page.inner_html("div.Receipt-container")
    return html
