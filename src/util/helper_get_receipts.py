import json
import os
from pathlib import Path
from app_settings import AppSettings, get_log
from utils import setup_context
from kroger import get_receipts
from parse_receipt import parse_receipt, output_receipt
from playwright.sync_api import sync_playwright


"""
Test script to verify get_receipts and parse_receipt functions using a local HTML files.
"""


# Get the project root directory (which is the parent of the 'src' directory)
project_root = Path(__file__).parent.parent.parent
settings = AppSettings()  # Initialize settings
log = get_log()  # Initialize logging
log.info(f"Project root directory: {project_root}")
purchases_url = f"file://{project_root}/tests/html/Purchase_History.html"
receipt_url = f"file://{project_root}/tests/html/Receipt3.html"

with sync_playwright() as p:
    browser, context = setup_context(p, settings)
    page = context.new_page()
    page.goto(purchases_url)
    receipts = get_receipts(page, purchases_url, purchases_url, settings)
    receipt_info = parse_receipt(page, receipt_url, "705~00851~2025-03-22~11~1131604")
    output_receipt(receipt_info, "test_data.json")

    # Added logic to log and remove test_data.json
    test_data_path = project_root / "test_data.json"
    if test_data_path.exists():
        with open(test_data_path, "r") as f:
            test_data_content = json.load(f)
            log.debug(
                f"Contents of test_data.json: {json.dumps(test_data_content, indent=2)}"
            )
        os.remove(test_data_path)
        log.info(f"Removed {test_data_path}")
    else:
        log.info(f"{test_data_path} does not exist.")
