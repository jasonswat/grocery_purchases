from pathlib import Path
from app_settings import AppSettings, log
from utils import setup_context
from kroger import get_receipts
from playwright.sync_api import sync_playwright


"""Test script to verify get_receipts function using a local HTML file."""


# Get the project root directory (which is the parent of the 'src' directory)
project_root = Path(__file__).parent.parent
settings = AppSettings()  # Initialize settings and logging
log.info(f"Project root directory: {project_root}")
purchases_url = f"file://{project_root}/tests/html/Purchase_History.html"


with sync_playwright() as p:
    browser, context = setup_context(p, settings)
    page = context.new_page()
    page.goto(purchases_url)
    receipts = get_receipts(page, purchases_url, purchases_url, settings)