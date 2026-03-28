import os
from random import randint
from time import sleep
from app_settings import get_log
from utils import move_mouse, setup_context
from bs4 import BeautifulSoup
from urllib.parse import urlparse

log = get_log()


def random_sleep(max_sleep):
    """Sleeps for a random amount of time."""
    if max_sleep < 1:
        return
    sleep_time = randint(1, max_sleep)
    log.debug(f"Sleeping for {sleep_time} seconds.")
    sleep(sleep_time)


def _perform_login(page, settings, success_url):
    """Fills out and submits the login form."""
    username = settings.kroger_username
    password = settings.kroger_password.get_secret_value()
    max_sleep = settings.max_sleep
    timeout = settings.timeout

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
    except Exception:
        log.info("Already signed in or not on the login page.")


def get_purchase_url(base_url, page_num):
    """Generates the URL for a specific page of purchases."""
    if base_url.startswith("file://"):
        path = base_url.replace("file://", "")
        # Look for p1.html, p2.html in the specified path
        file_path = os.path.join(path, f"p{page_num}.html")
        if os.path.exists(file_path):
            return f"file://{file_path}"
        return None
    else:
        # Standard live URL format
        return f"{base_url}?tab=purchases&page={page_num}"


def get_receipts(page, purchases_url, settings):
    max_sleep = settings.max_sleep
    pages_setting = settings.pages

    # Parse pages_setting
    target_pages = []
    limit = None
    if pages_setting == "all":
        limit = float("inf")
    elif pages_setting.startswith("max"):
        limit = int(pages_setting.replace("max", ""))
    else:
        try:
            target_pages = [int(pages_setting)]
        except ValueError:
            log.error(f"Invalid pages setting: {pages_setting}. Defaulting to page 1.")
            target_pages = [1]

    log.debug(f"Navigating to purchases url: {purchases_url}")
    page.goto(purchases_url)
    ensure_signed_in(page, settings, purchases_url)

    all_receipt_ids = []

    current_page_num = 1
    while True:
        # If we have specific pages to scrape, skip if not in list
        if target_pages and current_page_num not in target_pages:
            if current_page_num > max(target_pages):
                break
            current_page_num += 1
            continue

        # Generate URL for current page
        redirect_url = get_purchase_url(purchases_url, current_page_num)
        if not redirect_url:
            log.info(f"No more local files found for page {current_page_num}.")
            break

        log.info(f"Scraping page {current_page_num}: {redirect_url}")
        page.goto(redirect_url)
        try:
            page.wait_for_load_state("load")
            page.wait_for_selector("li.PO-NonPendingPurchase", timeout=10000)
        except Exception:
            log.info(f"No purchase items found on page {current_page_num} or timeout.")
            # If it's a live site, maybe we reached the end.
            # If it's local, we already checked existence.
            break

        soup = BeautifulSoup(page.content(), "html.parser")
        purchase_items = soup.select("li.PO-NonPendingPurchase")
        log.info(
            f"Found {len(purchase_items)} purchase items on page {current_page_num}."
        )

        page_receipt_ids = []
        for item in purchase_items:
            a_tag = item.find("a", href=True)
            if a_tag:
                # Extract ID from href: /mypurchases/detail/ID
                receipt_url = str(a_tag["href"])
                receipt_id = os.path.basename(urlparse(receipt_url).path)
                page_receipt_ids.append(receipt_id)

        all_receipt_ids.extend(page_receipt_ids)

        if limit and current_page_num >= limit:
            break

        if target_pages and current_page_num >= max(target_pages):
            break

        current_page_num += 1
        random_sleep(max_sleep)

    return all_receipt_ids


def sign_in(p, purchases_url, settings):
    timeout = settings.timeout
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
    timeout = settings.timeout
    max_sleep = settings.max_sleep
    page.goto(receipt_url, timeout=timeout)
    ensure_signed_in(page, settings, receipt_url)
    random_sleep(max_sleep)
    page.wait_for_load_state("load")
    page.wait_for_selector("div.Receipt-container")
    html = page.inner_html("div.Receipt-container")
    return html
