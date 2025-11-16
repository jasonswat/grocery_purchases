from app_settings import AppSettings, get_log
from kroger import get_receipts
from parse_receipt import parse_receipt, receipt_id_exists, output_receipt
from playwright.sync_api import sync_playwright
from utils import setup_context

log = get_log()


def main(settings: AppSettings):
    """Main function."""

    # kroger_domain = 'www.kroger.com' # should work on this site, but the receipt pages are slightly different, can't parse receipts yetceipts
    kroger_domain = "www.qfc.com"
    purchases_url = f"https://{kroger_domain}/mypurchases"
    # page that you want to go to after sign in
    # redirect_url = "https://www.qfc.com/mypurchases?tab=purchases&page=36"
    # redirect_url = "https://www.qfc.com/mypurchases?tab=purchases&page=1"
    redirect_url = "https://www.qfc.com/mypurchases?tab=purchases&page=3"

    with sync_playwright() as p:
        browser, context = setup_context(p, settings)
        page = context.new_page()
        try:
            receipts = get_receipts(page, purchases_url, redirect_url, settings)
            # For testing
            # receipts = ['705~00851~2023-04-04~500~1261444', '705~00851~2023-04-06~504~1841930', '705~00851~2023-04-07~504~1511846']
            for receipt_id in receipts:
                # Construct the receipt URL
                receipt_url = purchases_url + "/image/" + receipt_id
                # Check if the receipt already exists, if it does,
                # we log then skip to the next
                if receipt_id_exists("order_data.json", receipt_id):
                    log.info(
                        f"Receipt ID '{receipt_id}' already exists in 'order_data.json'. Skipping parsing."
                    )
                else:
                    log.info(
                        f"Receipt ID '{receipt_id}' does not exist in 'order_data.json'. Parsing receipt."
                    )
                    receipt_info = parse_receipt(page, receipt_url, receipt_id)
                    output_receipt(receipt_info, "order_data.json")
                    log.info(
                        f"Receipt ID '{receipt_id}' parsed and saved to 'order_data.json'."
                    )
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    log = get_log()
    settings = AppSettings()
    log.info("Starting the application..")
    main(settings=settings)
