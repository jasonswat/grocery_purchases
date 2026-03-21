import json
import os
import pytest
from bs4 import BeautifulSoup, Tag
from parse_receipt import (
    _h2_item_details,
    _span_text_pred,
    _span_contains_pattern,
    receipt_id_exists,
    parse_price_and_quantity,
    extract_upc,
    remove_symbols,
    format_date,
    parse_items,
    parse_receipt,
    extract_span_text,
    output_receipt,
)
from unittest.mock import MagicMock, patch


def test_h2_item_details():
    soup = BeautifulSoup(
        "<h2>Item Details</h2><h2>Other</h2><span>Not H2</span>", "html.parser"
    )
    h2_tags = soup.find_all("h2")
    span_tag = soup.find("span")

    assert _h2_item_details(h2_tags[0]) is True
    assert _h2_item_details(h2_tags[1]) is False
    assert _h2_item_details(span_tag) is False
    assert _h2_item_details("not a tag") is False


def test_span_text_pred():
    soup = BeautifulSoup(
        "<span>Target</span><span>Other</span><div>Not Span</div>", "html.parser"
    )
    pred = _span_text_pred("Target")

    spans = soup.find_all("span")
    div = soup.find("div")

    assert pred(spans[0]) is True
    assert pred(spans[1]) is False
    assert pred(div) is False
    assert pred("not a tag") is False


def test_span_contains_pattern():
    soup = BeautifulSoup("<span>1 x $5.00</span><span>Other</span>", "html.parser")
    pred = _span_contains_pattern(r"\d+ x \$")

    spans = soup.find_all("span")

    assert pred(spans[0]) is True
    assert pred(spans[1]) is False
    assert pred("not a tag") is False


def test_receipt_id_exists(tmp_path):
    file_path = tmp_path / "receipts.json"
    receipts = [{"receipt_id": "123"}, {"receipt_id": "456"}]

    with open(file_path, "w") as f:
        json.dump(receipts, f)

    assert receipt_id_exists(str(file_path), "123") is True
    assert receipt_id_exists(str(file_path), "789") is False

    # Test FileNotFoundError
    assert receipt_id_exists("non_existent.json", "123") is False

    # Test JSONDecodeError
    invalid_file = tmp_path / "invalid.json"
    invalid_file.write_text("not json")
    assert receipt_id_exists(str(invalid_file), "123") is False


def test_parse_price_and_quantity():
    # Format 1
    assert parse_price_and_quantity("2 x $3.99") == (2, None, 3.99)
    assert parse_price_and_quantity("3 x $1.50each") == (3, None, 1.50)

    # Format 2
    assert parse_price_and_quantity("1.28 lbs x $7.99 each (approx.)") == (
        None,
        1.28,
        7.99,
    )
    assert parse_price_and_quantity("0.5 lbs x $4.00 each") == (None, 0.5, 4.00)

    # Invalid format
    with pytest.raises(ValueError, match="Invalid price string format"):
        parse_price_and_quantity("invalid")


def test_extract_upc():
    assert extract_upc("UPC: 000111222333") == "000111222333"
    assert extract_upc("No UPC here") is None


def test_remove_symbols():
    assert remove_symbols("$12.34") == "12.34"
    assert remove_symbols("12.34") == "12.34"


def test_format_date():
    assert format_date("Sep. 10, 2025", "%b. %d, %Y") == "2025-09-10"
    assert format_date("Invalid Date", "%b. %d, %Y") is None


def test_parse_items():
    html = """
    <div>
        <div><h2>Item Details</h2></div>
        <div style="break-inside: avoid;">
            <span data-citrus-component="Text" class="font-medium">Apples</span>
            <span>$2.50</span>
            <span>2 x $1.25<span class="line-through">$3.00</span></span>
            <span>UPC: 12345</span>
        </div>
        <div style="break-inside: avoid;">
            <span data-citrus-component="Text" class="font-medium">Milk</span>
            <span>$4.00</span>
            <span>1 x $4.00</span>
            <span>UPC: 67890</span>
        </div>
        <div style="break-inside: avoid;">
            <!-- Missing item name, should be skipped -->
            <span>Something else</span>
        </div>
    </div>
    """
    soup = BeautifulSoup(html, "html.parser")
    items = parse_items(soup)

    assert len(items) == 2
    assert items[0]["item_name"] == "Apples"
    assert items[0]["price"] == 2.50
    assert items[0]["quantity"] == 2
    assert items[0]["original_price"] == 3.00
    assert items[0]["upc_id"] == "12345"

    assert items[1]["item_name"] == "Milk"
    assert items[1]["price"] == 4.00
    assert items[1]["quantity"] == 1
    assert items[1]["upc_id"] == "67890"


def test_parse_items_no_price_no_upc():
    html = """
    <div>
        <div><h2>Item Details</h2></div>
        <div style="break-inside: avoid;">
            <span data-citrus-component="Text" class="font-medium">Mystery Item</span>
        </div>
    </div>
    """
    soup = BeautifulSoup(html, "html.parser")
    items = parse_items(soup)
    assert items[0]["item_name"] == "Mystery Item"
    assert items[0]["price"] is None
    assert items[0]["upc_id"] is None


def test_parse_items_exception():
    # Trigger an exception during parsing a specific item
    html = """
    <div>
        <div><h2>Item Details</h2></div>
        <div style="break-inside: avoid;">
            <span data-citrus-component="Text" class="font-medium">Good Item</span>
            <span>$1.00</span>
        </div>
        <div style="break-inside: avoid;">
            <span data-citrus-component="Text" class="font-medium">Bad Item</span>
            <span>$invalid</span>
        </div>
    </div>
    """
    soup = BeautifulSoup(html, "html.parser")
    # We need to mock remove_symbols to raise an exception for the bad item
    with patch("parse_receipt.remove_symbols") as mock_remove:
        mock_remove.side_effect = ["1.00", Exception("Parsing error")]
        items = parse_items(soup)
        assert len(items) == 1
        assert items[0]["item_name"] == "Good Item"


def test_parse_items_no_items():
    html = "<div><h2>Item Details</h2></div>"
    soup = BeautifulSoup(html, "html.parser")
    with pytest.raises(ValueError, match="Could not parse any items"):
        parse_items(soup)


def test_parse_items_no_header():
    html = "<div></div>"
    soup = BeautifulSoup(html, "html.parser")
    with pytest.raises(ValueError, match="Could not find 'Item Details'"):
        parse_items(soup)


def test_extract_span_text():
    html = "<div><span>Label</span><span>Value</span></div>"
    soup = BeautifulSoup(html, "html.parser")
    assert extract_span_text(soup, "Label") == "Value"


def test_output_receipt(tmp_path):
    output_file = tmp_path / "output.json"
    receipt_info = {
        "receipt_id": "123",
        "date": "2025-03-22",
        "total": "10.00",
        "tax": "1.00",
        "items": [],
    }

    # Test file doesn't exist
    output_receipt(receipt_info, str(output_file))
    with open(output_file, "r") as f:
        data = json.load(f)
        assert len(data) == 1
        assert data[0]["receipt_id"] == "123"

    # Test file exists and is a list
    receipt_info2 = receipt_info.copy()
    receipt_info2["receipt_id"] = "456"
    output_receipt(receipt_info2, str(output_file))
    with open(output_file, "r") as f:
        data = json.load(f)
        assert len(data) == 2
        assert data[1]["receipt_id"] == "456"

    # Test file exists and is not a list (edge case in code)
    output_file_dict = tmp_path / "output_dict.json"
    with open(output_file_dict, "w") as f:
        json.dump(receipt_info, f)

    output_receipt(receipt_info2, str(output_file_dict))
    with open(output_file_dict, "r") as f:
        data = json.load(f)
        assert isinstance(data, list)
        assert len(data) == 2

    # Test JSONDecodeError (corrupt file)
    corrupt_file = tmp_path / "corrupt.json"
    corrupt_file.write_text("invalid json")
    output_receipt(receipt_info, str(corrupt_file))
    with open(corrupt_file, "r") as f:
        data = json.load(f)
        assert len(data) == 1


@patch("parse_receipt.parse_items")
def test_parse_receipt(mock_parse_items):
    mock_parse_items.return_value = [{"item_name": "Test Item"}]
    mock_page = MagicMock()
    mock_page.content.return_value = """
    <div>
        <span>Order Date: </span>Sep. 22, 2025
        <span>Order Total</span><span>$11.00</span>
        <span>Sales Tax</span><span>$1.00</span>
    </div>
    """

    receipt_info = parse_receipt(
        mock_page, "http://fake.com", "705~00851~2025-03-22~1~1"
    )

    assert receipt_info["date"] == "2025-09-22"
    assert receipt_info["total"] == "11.00"
    assert receipt_info["tax"] == "1.00"
    assert receipt_info["items"] == [{"item_name": "Test Item"}]


@patch("parse_receipt.parse_items")
def test_parse_receipt_date_from_id(mock_parse_items):
    mock_parse_items.return_value = []
    mock_page = MagicMock()
    # No Order Date span
    mock_page.content.return_value = """
    <div>
        <span>Order Total</span><span>$11.00</span>
        <span>Sales Tax</span><span>$1.00</span>
    </div>
    """

    receipt_info = parse_receipt(
        mock_page, "http://fake.com", "705~00851~2025-03-22~1~1"
    )

    assert receipt_info["date"] == "2025-03-22"
