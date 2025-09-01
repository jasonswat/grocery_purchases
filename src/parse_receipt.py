import re
import json
import logging
from random import randint
from time import sleep
from datetime import datetime
from bs4 import BeautifulSoup
from typing import List, Dict, Any

def receipt_id_exists(filename: str, receipt_id: str) -> bool:
    logging.info(f"Checking if receipt ID '{receipt_id}' exists in '{filename}'.")
    try:
        with open(filename, 'r') as f:
            receipts: List[Dict[str, Any]] = json.load(f)
    except FileNotFoundError:
        logging.error(f"Error: File '{filename}' not found.")
        return False
    except json.JSONDecodeError:
        logging.error(f"Error: File '{filename}' is not a valid JSON file.")
        return False
    for record in receipts:
        if record.get('receipt_id') == receipt_id:
            return True
    return False

def parse_price_and_quantity(price_and_quantity: str):
    # Format 1: "quantity x $price"
    match1 = re.match(r"(\d+\.?\d*)\s*\s*x\s*\$(\d+\.?\d*)(\s)?(each)?", price_and_quantity)
    if match1:
        quantity = int(match1.group(1))
        price = float(match1.group(2))
        weight = None  # No weight in this format
        return quantity, weight, price

    # Format 2: "weight lbs x $price each (approx.)"
    match2 = re.match(r"(\d+\.?\d*)\s*lbs\s*x\s*\$(\d+\.?\d*)\s*(each)?", price_and_quantity)
    if match2:
        weight = float(match2.group(1))
        price = float(match2.group(2))
        quantity = None  # No quantity in this format
        return quantity, weight, price

    raise ValueError("Invalid price string format for {}".format(price_and_quantity))

def extract_upc(upc_string):
    match = re.match(r"UPC:\s*(\d+)", upc_string)
    if match:
        return match.group(1)

def parse_items(soup):
    items = []
    item_groups = soup.find_all('div', class_='mt-8 mb-4')
    for item_group in item_groups:
        item_name = item_group.find('span', class_="kds-Text--m kds-Text--bold").text
        if item_group.find('span', class_='line-through'):
            # item will only have original price if it's a markdown
            original_price = item_group.find('span', class_='line-through').text
            original_price = remove_symbols(original_price)
        else:
            original_price = None
        price_group = item_group.select('span.kds-Text--m:not(.kds-Text--bold)')
        price_and_quantity = price_group[1].contents[0]
        item_upc = item_group.find('div', class_='ml-12 mt-4 font-secondary body-s text-neutral-most-prominent').text
        upc_id = extract_upc(item_upc)
        quantity, weight, price = parse_price_and_quantity(price_and_quantity)
        item = { "upc_id": upc_id, "item_name": item_name, "quantity": quantity, "weight": weight, "price": price, "original_price": original_price }
        items.append(item)
        # print(item)
    return items

def remove_symbols(text_string):
    for char in "$":
        text_string = text_string.replace(char, "")
    return text_string

def format_date(date_string, current_format = "%B %d, %Y"): # March 22, 2025
    try:
        date_object = datetime.strptime(date_string, current_format)
        return date_object.strftime("%Y-%m-%d")
    except ValueError:
        return None

def extract_span_text(soup, span_string):
    # Search for the string and work backwards to get the total
    find_span = soup.find('span', string=span_string)
    span_text = find_span.next_sibling.text
    return span_text

def output_receipt(receipt_id, receipt_date, receipt_total, receipt_tax, receipt_items, output_file):
    logging.info(f"Writing receipt ID: {receipt_id} to {output_file}")
    receipt_data = {
        "receipt_id": receipt_id,
        "date": receipt_date,
        "total": receipt_total,
        "tax": receipt_tax,
        "items": receipt_items
    }
    try:
        with open(output_file, 'r+') as f:
            try:
                receipts = json.load(f)
            except json.JSONDecodeError:
                receipts = [] #file is empty or corrupt
            if isinstance(receipts, list):
                receipts.append(receipt_data)
            else:
                receipts = [receipts, receipt_data] # the json file was a single dictionary, convert to a list
            f.seek(0)  # Go back to the beginning of the file
            json.dump(receipts, f, indent=None)
            f.truncate() #remove the old content
    except FileNotFoundError:
        # File doesn't exist, create it and write the receipt
        with open(output_file, 'w') as f:
            json.dump([receipt_data], f, indent=None) # Use indent=4 for pretty printing, indent=None for compact

def parse_receipt(page, base_url, receipt_id, output_file):
    logging.info(f"Parsing receipt ID: {receipt_id}")
    receipt_url = base_url + receipt_id
    # Check if receipt_id exists
    if receipt_id_exists(output_file, receipt_id):
        return f"Receipt ID '{receipt_id}' already exists in '{output_file}'."
    else:
        logging.info(f"Receipt ID '{receipt_id}' does not exist in '{output_file}' getting contents of receipt.")
        sleep(randint(3,20))
        page.goto(receipt_url)
        sleep(randint(3,20))
        page.is_visible('div.PH-ProductCard-container')
        html = page.inner_html('#receipt-print-area')
        soup = BeautifulSoup(html, 'html.parser')
        receipt_total = extract_span_text(soup, "Order Total")
        receipt_total = remove_symbols(receipt_total)
        receipt_date = extract_span_text(soup, "Order Date: ")
        receipt_date = format_date(receipt_date)
        receipt_tax = extract_span_text(soup, "Sales Tax")
        receipt_tax = remove_symbols(receipt_tax)
        receipt_items = parse_items(soup)
        logging.info(f"Receipt ID: {receipt_id} items gathered, writing receipt to {output_file}")
        output_receipt(receipt_id, receipt_date, receipt_total, receipt_tax, receipt_items, output_file)
        return f"Receipt ID '{receipt_id}' parsed and saved to '{output_file}'."