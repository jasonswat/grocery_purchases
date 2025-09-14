import re
import json
from app_settings import get_log
from random import randint
from time import sleep
from datetime import datetime
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional, Union, TypedDict


log = get_log()


class ReceiptInfo(TypedDict):
    receipt_id: str
    date: Optional[str]
    total: str
    tax: str
    items: List[Dict[str, Any]]


def receipt_id_exists(filename: str, receipt_id: str) -> bool:
    log.info(f"Checking if receipt ID '{receipt_id}' exists in '{filename}'.")
    try:
        with open(filename, 'r') as f:
            receipts: List[Dict[str, Any]] = json.load(f)
    except FileNotFoundError:
        log.error(f"Error: File '{filename}' not found.")
        return False
    except json.JSONDecodeError:
        log.error(f"Error: File '{filename}' is not a valid JSON file.")
        return False
    for record in receipts:
        if record.get('receipt_id') == receipt_id:
            return True
    return False


def parse_price_and_quantity(price_and_quantity: str) -> tuple[Optional[int], Optional[float], float]:
    quantity: Union[int, None]
    weight: Union[float, None]
    # Format 1: "quantity x $price"
    # Example: "2 x $3.99"
    match1 = re.match(r"(\d+\.?\d*)\s*\s*x\s*\$(\d+\.?\d*)(\s)?(each)?", price_and_quantity)
    # Format 2: "weight lbs x $price each (approx.)"
    # Example: "1.28 lbs x $7.99 each (approx.)"
    match2 = re.match(r"(\d+\.?\d*)\s*lbs\s*x\s*\$(\d+\.?\d*)(\s*each)?(\s*\(approx\.\))?", price_and_quantity)
    if match1:
        quantity = int(match1.group(1))
        price = float(match1.group(2))
        weight = None  # No weight in this format
        return quantity, weight, price
    elif match2:
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
    if not item_groups:
        log.error("No item groups found in receipt. Unable to parse items.")
        raise ValueError("No item groups found in receipt.")
    for item_group in item_groups:
        try:
            item_name = item_group.find('span', class_="kds-Text--m kds-Text--bold").text
            original_price = None
            log.debug(f"Item name: {item_name}")
            line_through_span = item_group.find('span', class_='line-through')
            if line_through_span:
                # item will only have original price if it's a markdown
                original_price = line_through_span.text
                original_price = remove_symbols(original_price)
            price_group = item_group.select('span.kds-Text--m:not(.kds-Text--bold)')
            price_and_quantity = price_group[1].contents[0]
            log.debug(f"Price and quantity: {price_and_quantity}")
            item_upc = item_group.find('div', class_='ml-12 mt-4 font-secondary body-s text-neutral-most-prominent').text
            upc_id = extract_upc(item_upc)
            quantity, weight, price = parse_price_and_quantity(price_and_quantity)
            item: Dict[str, Any] = {"upc_id": upc_id, "item_name": item_name, "quantity": quantity, "weight": weight, "price": price, "original_price": original_price}
            items.append(item)
            log.debug(f"Added item to list: {item}")
        except (AttributeError, IndexError) as e:
            log.warning(f"Could not parse an item, skipping. Error: {e}")
            continue
    if not items:
        log.error("Could not parse any items from the receipt.")
        raise ValueError("Could not parse any items from the receipt.")
    return items


def remove_symbols(text_string):
    for char in "$":
        text_string = text_string.replace(char, "")
    return text_string


def format_date(date_string, current_format="%b. %d, %Y"):  # March 22, 2025
    """"
    Convert date string to YYYY-MM-DD format
    Default format is "Month DD, YYYY"
    Example input:
    <span class="font-bold">Order Date: </span>
    Sep. 10, 2025
    </span>
    """
    try:
        date_object = datetime.strptime(date_string, current_format)
        return date_object.strftime("%Y-%m-%d")
    except ValueError:
        return None


def extract_span_text(soup, span_string):
    # Search for the string and work backwards to get the total
    find_span = soup.find('span', string=span_string)
    span_text = find_span.find_next_sibling().text
    return span_text


def output_receipt(receipt_info: ReceiptInfo, output_file: str):
    log.info(f"Function: output_receipt, writing receipt ID: {receipt_info['receipt_id']} to {output_file}")
    receipt_data = {
        "receipt_id": receipt_info['receipt_id'],
        "date": receipt_info['date'],
        "total": receipt_info['total'],
        "tax": receipt_info['tax'],
        "items": receipt_info['items']
    }
    log.debug(f"Function: output_receipt, receipt data: {receipt_data}")
    try:
        with open(output_file, 'r+') as f:
            try:
                receipts = json.load(f)
            except json.JSONDecodeError:
                receipts = []  # File is empty or corrupt
                log.warning(f"Function: output_receipt, file '{output_file}' is empty or corrupt. Starting a new list.")
            if isinstance(receipts, list):
                receipts.append(receipt_data)
            else:
                receipts = [receipts, receipt_data]  # The json file was a single dictionary, convert to a list
            f.seek(0)  # Go back to the beginning of the file
            json.dump(receipts, f, indent=None)
            f.truncate()  # Remove the old content
    except FileNotFoundError:
        log.info(f"File '{output_file}' not found, creating file.")
        # File doesn't exist, create it and write the receipt
        with open(output_file, 'w') as f:
            json.dump([receipt_data], f, indent=None)  # Use indent=4 for pretty printing, indent=None for compact


def parse_receipt(page, receipt_url, receipt_id) -> ReceiptInfo:
    sleep(randint(3, 20))
    page.goto(receipt_url)
    sleep(randint(3, 20))
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
    
    receipt_info: ReceiptInfo = {
        "receipt_id": receipt_id,
        "date": receipt_date,
        "total": receipt_total,
        "tax": receipt_tax,
        "items": receipt_items
    }
    return receipt_info
