from app_settings import AppSettings, get_log
from kroger import get_receipts, sign_in
from parse_receipt import parse_receipt, receipt_id_exists
from playwright.sync_api import sync_playwright

log = get_log()

def main(settings: AppSettings):

    """Main function."""

    kroger_domain = 'www.qfc.com'  # This will hopefully work at fredmeyer.com or other kroger stores as well
    purchases_url = f"https://{kroger_domain}/mypurchases"
    # redirect_url = "https://www.qfc.com/mypurchases?tab=purchases&page=36"
    redirect_url = "https://www.qfc.com/mypurchases?tab=purchases&page=1"

    with sync_playwright() as p:
        browser, context, page = sign_in(p, purchases_url, settings)
        base_url = f"https://{kroger_domain}/mypurchases/image/"
        try:
            receipts = get_receipts(page, purchases_url, redirect_url, settings)
            # For testing
            # receipts = ['705~00851~2023-04-04~500~1261444', '705~00851~2023-04-06~504~1841930', '705~00851~2023-04-07~504~1511846']
            for receipt_id in receipts:
                # Construct the receipt URL
                receipt_url = base_url + receipt_id
                # Check if the receipt already exists, if it does,
                # we log then skip to the next
                if receipt_id_exists("order_data.json", receipt_id):
                    log.info(f"Receipt ID '{receipt_id}' already exists in 'order_data.json'. Skipping parsing.")
                else:
                    log.info(f"Receipt ID '{receipt_id}' does not exist in 'order_data.json'. Parsing receipt.")
                    parse_receipt(page, receipt_url, receipt_id, "order_data.json")
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    log = get_log()
    settings = AppSettings()
    log.info("Starting the application..")
    main(settings=settings)
