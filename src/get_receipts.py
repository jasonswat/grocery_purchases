import os
from app_settings import log
from random import randint
from time import sleep
from bs4 import BeautifulSoup
from urllib.parse import urlparse


def get_basename_from_url(url):
    parsed_url = urlparse(url)
    return os.path.basename(parsed_url.path)

def get_receipts(page, purchases_url, redirect_url):
    page.goto(purchases_url)
    sleep(randint(3,30))
    page.wait_for_load_state('load')
    page.is_visible('div.PurchaseResultsColumn')
    page.goto(redirect_url)
    sleep(randint(3,30))
    page.wait_for_load_state('load')
    page.is_visible('div.PurchaseResultsColumn')
    html = page.inner_html('#PurchaseResultsColumn')
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a', {'class': 'kds-Link kds-Link--inherit kds-Link--implied block p-16 text-neutral-most-prominent no-underline sm:py-24'})
    #print(f"Links: {links}")
    receipts = []
    for a in links:
        #print(a)
        receipt_id = get_basename_from_url(a['href'])
        receipts.append(receipt_id)
    log.info(f"Found {len(receipts)} receipts {receipts}.")
    return receipts