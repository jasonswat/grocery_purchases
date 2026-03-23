import re
import json
from app_settings import get_log
from random import randint
from time import sleep
from datetime import datetime
from bs4 import BeautifulSoup, Tag
from typing import List, Dict, Any, Optional, Union, TypedDict, Pattern, Callable
from pathlib import Path


log = get_log()


def _h2_item_details(tag: Any) -> bool:
    if not isinstance(tag, Tag):
        return False
    if tag.name != "h2":
        return False
    return tag.string == "Item Details" if tag.string is not None else False


def _span_text_pred(text: str) -> Callable[[Any], bool]:
    def _pred(tag: Any) -> bool:
        if not isinstance(tag, Tag):
            return False
        if tag.name != "span":
            return False
        return tag.get_text().strip() == text

    return _pred


def _span_contains_pattern(pattern: Union[str, Pattern[str]]) -> Callable[[Any], bool]:
    def _pred(tag: Any) -> bool:
        if not isinstance(tag, Tag):
            return False
        if tag.name != "span":
            return False
        return bool(re.search(pattern, tag.get_text() or ""))

    return _pred


class ReceiptInfo(TypedDict):
    receipt_id: str
    date: Optional[str]
    total: str
    tax: str
    items: List[Dict[str, Any]]
    store_name: Optional[str]
    store_id: Optional[str]
    order_type: str


def receipt_id_exists(filename: str, receipt_id: str) -> bool:
    """
    Check if a receipt ID exists. For partitioned storage, filename is ignored
    and we check for the existence of the receipt file in output/receipts/.
    Arguments:
        filename: (Deprecated) path to the JSON file
        receipt_id: ID of the receipt to check
    Returns: True if the receipt ID exists, False otherwise
    """
    receipt_path = Path("output/receipts") / f"{receipt_id}.json"
    exists = receipt_path.exists()
    if exists:
        log.info(f"Receipt ID '{receipt_id}' already exists at {receipt_path}")
    return exists


def parse_price_and_quantity(
    price_and_quantity: str,
) -> tuple[Optional[int], Optional[float], float]:
    """
    Parses a price and quantity string to extract quantity, weight, and price.
    Arguments:
        price_and_quantity: string containing price and quantity information
    Returns: tuple containing quantity (int or None), weight (float or None), and price (float)
    Format 1 "quantity x $price" example inputs:
       "2 x $3.99"
       "3 x $1.50"
    Format 2 "weight lbs x $price each (approx.)" example inputs:
       "1.28 lbs x $7.99 each (approx.)"
       "0.5 lbs x $4.00 each (approx.)"
    Format 1 example outputs:
       (2, None, 3.99)
       (3, None, 1.50)
    Format 2 example outputs:
       (None, 1.28, 7.99)
       (None, 0.5, 4.00)
    """
    quantity: Union[int, None]
    weight: Union[float, None]
    # Format 1: "quantity x $price" match
    match1 = re.match(
        r"(\d+\.?\d*)\s*\s*x\s*\$(\d+\.?\d*)(\s)?(each)?", price_and_quantity
    )
    # Format 2: "weight lbs x $price each (approx.)" match
    match2 = re.match(
        r"(\d+\.?\d*)\s*lbs\s*x\s*\$(\d+\.?\d*)(\s*each)?(\s*\(approx\.\))?",
        price_and_quantity,
    )
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
    """Extracts the UPC code from a string.
    Arguments:
        upc_string: string containing the UPC code
    Returns: UPC code as a string or None if not found
    Example input: "UPC: 000111222333"
    Example output: "000111222333"
    """
    match = re.match(r"UPC:\s*(\d+)", upc_string)
    if match:
        return match.group(1)


def parse_items(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """
    Parses items from the receipt HTML data.
    Arguments:
        soup: A BeautifulSoup object representing the receipt HTML.
    Returns: A list of dictionaries, where each dictionary represents an item.
    """
    items = []

    item_details_header = soup.find(_h2_item_details)
    if not item_details_header:
        raise ValueError("Could not find 'Item Details' section in receipt HTML.")

    # All items are in divs with `break-inside: avoid` style
    item_containers: List[Any] = []
    if item_details_header.parent:
        item_containers = item_details_header.parent.find_next_siblings(
            "div", style="break-inside: avoid;"
        )

    for container in item_containers:
        if not isinstance(container, Tag):
            continue
        try:
            item_name_element = container.find(
                name="span",
                attrs={"data-citrus-component": "Text", "class": "font-medium"},
            )
            if not item_name_element:
                continue

            item_name = item_name_element.text.strip()

            price_element = item_name_element.find_next_sibling(name="span")
            price = (
                float(remove_symbols(price_element.text.strip()))
                if price_element
                else None
            )

            quantity = 1  # default
            original_price = None

            quantity_str_element = container.find(_span_contains_pattern(r"\s*x\s*\$"))
            if quantity_str_element:
                # `quantity_str_element` can be a Tag or a NavigableString; normalize text
                if isinstance(quantity_str_element, Tag):
                    quantity_text = quantity_str_element.text
                else:
                    quantity_text = str(quantity_str_element)

                quantity_match = re.match(r"(\d+)", quantity_text)
                if quantity_match:
                    quantity = int(quantity_match.group(1))

                # Only call `.find` if we have a Tag
                if isinstance(quantity_str_element, Tag):
                    original_price_element = quantity_str_element.find(
                        name="span", class_="line-through"
                    )
                    if original_price_element:
                        original_price = float(
                            remove_symbols(original_price_element.text.strip())
                        )

            upc_element = container.find(string=re.compile(r"UPC: \d+"))
            upc_id = extract_upc(upc_element) if upc_element else None

            item: Dict[str, Any] = {
                "upc_id": upc_id,
                "item_name": item_name,
                "quantity": quantity,
                "weight": None,
                "price": price,
                "original_price": original_price,
            }
            items.append(item)
            log.debug(f"Added item to list: {item}")

        except Exception as e:
            log.warning(f"Could not parse an item from HTML, skipping. Error: {e}")
            continue

    if not items:
        log.error("Could not parse any items from the receipt HTML.")
        raise ValueError("Could not parse any items from the receipt HTML.")

    return items


def remove_symbols(text_string):
    """
    Removes dollar signs($) from a string.
    Arguments:
        text_string: string to clean
    Returns: cleaned string
    """
    for char in "$":
        text_string = text_string.replace(char, "")
    return text_string


def format_date(date_string, current_format="%b. %d, %Y"):  # March 22, 2025
    """
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
    """
    Extract text from a span element based on a given string.
    Arguments:
        soup: BeautifulSoup object
        span_string: string to search for in the span
    Returns: text of the next sibling span element after the given string
    """
    find_span = soup.find(_span_text_pred(span_string))
    span_text = find_span.find_next_sibling().text
    return span_text


def output_receipt(receipt_info: ReceiptInfo, output_file: str):
    """
    Write receipt information to an individual JSON file in output/receipts/.
    Arguments:
        receipt_info: dictionary containing receipt information
        output_file: (Deprecated) path to the output JSON file
    """
    receipt_id = receipt_info["receipt_id"]
    output_dir = Path("output/receipts")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{receipt_id}.json"

    log.info(
        f"Function: output_receipt, writing receipt ID: {receipt_id} to {output_path}"
    )

    receipt_data = {
        "receipt_id": receipt_info["receipt_id"],
        "date": receipt_info["date"],
        "total": receipt_info["total"],
        "tax": receipt_info["tax"],
        "store_name": receipt_info.get("store_name"),
        "store_id": receipt_info.get("store_id"),
        "order_type": receipt_info.get("order_type", "Unknown"),
        "items": receipt_info["items"],
    }

    try:
        with open(output_path, "w") as f:
            json.dump(receipt_data, f, indent=4)
    except Exception as e:
        log.error(f"Failed to write receipt {receipt_id} to {output_path}: {e}")


def parse_receipt(page, receipt_url, receipt_id) -> ReceiptInfo:
    """
    Parse receipt information from a given URL by extracting the data from the HTML.
    Arguments:
        page: Playwright page object
        receipt_url: URL of the receipt to parse
        receipt_id: ID of the receipt
    Returns: dictionary containing receipt information
    """
    log.info(f"Parsing receipt {receipt_id} from {receipt_url}")
    page.goto(receipt_url)
    page.wait_for_load_state("load")
    sleep(randint(3, 5))
    html = page.content()
    soup = BeautifulSoup(html, "html.parser")

    # Find store info and order type
    store_name = None
    store_id = None
    order_type = "In-Store"  # Default

    # Extract store_id from receipt_id if format is "banner~store~date~..."
    id_parts = receipt_id.split("~")
    if len(id_parts) >= 2:
        store_id = id_parts[1]

    # Look for Banner Name in script tags
    banner_match = re.search(r'window\.__BANNER_NAME__\s*=\s*"([^"]+)"', html)
    if banner_match:
        store_name = banner_match.group(1).upper()

    # Determine order type
    # If "TERMINAL ID" exists, it's definitely In-Store.
    # Otherwise check for common online keywords
    terminal_element = soup.find(string=re.compile(r"TERMINAL ID", re.I))
    if not terminal_element:
        # Check for online indicators in the HTML
        if soup.find(string=re.compile(r"Pickup|Pick up", re.I)):
            order_type = "Pickup"
        elif soup.find(string=re.compile(r"Delivery", re.I)):
            order_type = "Delivery"

    # Find date
    date_str_element = soup.find(_span_contains_pattern(r"Order Date: "))
    date_str = None
    if date_str_element:
        date_sibling = date_str_element.find_next_sibling(string=True)
        date_str = str(date_sibling).strip() if date_sibling else None

    if date_str:
        # The string is like "Dec. 5, 2025"
        receipt_date = format_date(date_str, "%b. %d, %Y")
    else:
        receipt_date = id_parts[2] if len(id_parts) > 2 else None

    # Find total
    total_element = soup.find(_span_text_pred("Order Total"))
    receipt_total = "0.00"
    if total_element:
        total_sibling = total_element.find_next_sibling()
        if total_sibling:
            receipt_total = total_sibling.text.strip()

    # Find tax
    tax_element = soup.find(_span_text_pred("Sales Tax"))
    receipt_tax = "0.00"
    if tax_element:
        tax_sibling = tax_element.find_next_sibling()
        if tax_sibling:
            receipt_tax = tax_sibling.text.strip()

    receipt_items = parse_items(soup)

    receipt_info: ReceiptInfo = {
        "receipt_id": receipt_id,
        "date": receipt_date,
        "total": remove_symbols(receipt_total),
        "tax": remove_symbols(receipt_tax),
        "items": receipt_items,
        "store_name": store_name,
        "store_id": store_id,
        "order_type": order_type,
    }
    return receipt_info
