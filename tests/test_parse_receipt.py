from parse_receipt import format_date, extract_span_text, parse_receipt
from bs4 import BeautifulSoup
from unittest.mock import MagicMock, patch


def test_format_date():
    assert format_date("Sep. 10, 2025", "%b. %d, %Y") == "2025-09-10"


def test_extract_span_text():
    html = """
    <div>
        <span class="font-bold">Order Total</span>
        <span>$123.45</span>
    </div>
    """
    soup = BeautifulSoup(html, "html.parser")
    total = extract_span_text(soup, "Order Total")
    assert total == "$123.45"


@patch("parse_receipt.parse_items", return_value=[])
def test_parse_receipt_date_from_id(mock_parse_items):
    # Arrange
    mock_page = MagicMock()
    receipt_id = "705~00851~2025-03-22~11~1131604"
    receipt_url = "http://fake.com/receipt"

    mock_page.inner_html.return_value = """
    <div id="receipt-print-area">
        <div>
            <span class="font-bold">Order Total</span>
            <span>$40.67</span>
        </div>
        <div>
            <span class="font-bold">Sales Tax</span>
            <span>$0.00</span>
        </div>
    </div>
    """

    # Act
    receipt_info = parse_receipt(mock_page, receipt_url, receipt_id)

    # Assert
    assert receipt_info["date"] == "2025-03-22"
    mock_parse_items.assert_called_once()
