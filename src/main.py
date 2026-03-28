from app_settings import AppSettings, get_log
from kroger import get_receipts
from parse_receipt import parse_receipt, receipt_id_exists, output_receipt
from playwright.sync_api import sync_playwright
from utils import setup_context

log = get_log()


def main(settings: AppSettings):
    """Main function."""

    # kroger_domain = 'www.kroger.com' # should work on this site, but the receipt pages are slightly different, can't parse receipts yet
    kroger_domain = "www.qfc.com"
    purchases_url = f"https://{kroger_domain}/mypurchases"

    # Handle PAGES setting
    pages_to_scrape = settings.pages
    log.info(f"Pages to scrape: {pages_to_scrape}")

    with sync_playwright() as p:
        browser, context = setup_context(p, settings)
        page = context.new_page()
        try:
            # get_receipts now handles multiple pages based on settings.pages
            receipt_ids = get_receipts(page, purchases_url, settings)
            log.info(f"Total receipts found: {len(receipt_ids)}")

            for receipt_id in receipt_ids:
                # Construct the receipt URL
                receipt_url = purchases_url + "/image/" + receipt_id
                # Check if the receipt already exists, if it does,
                # we log then skip to the next
                if receipt_id_exists("", receipt_id):
                    log.info(
                        f"Receipt ID '{receipt_id}' already exists. Skipping parsing."
                    )
                else:
                    log.info(
                        f"Receipt ID '{receipt_id}' does not exist. Parsing receipt."
                    )
                    try:
                        receipt_info = parse_receipt(page, receipt_url, receipt_id)
                    except Exception as e:
                        log.error(f"Failed to parse receipt {receipt_id}: {e}")
                        continue
                    output_receipt(receipt_info, "")
                    log.info(f"Receipt ID '{receipt_id}' parsed and saved.")
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    log = get_log()
    settings = AppSettings()
    log.info("Starting the application..")
    main(settings=settings)
