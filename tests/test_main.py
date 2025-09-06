from unittest.mock import MagicMock, patch

import pytest

from app_settings import AppSettings
from main import main


@patch("main.parse_receipt")
@patch("main.get_receipts")
@patch("main.sign_in")
@patch("main.sync_playwright")
def test_main_happy_path(mock_sync_playwright, mock_sign_in, mock_get_receipts, mock_parse_receipt):
    """Test the main function in a happy path scenario."""
    # Arrange
    mock_settings = MagicMock(spec=AppSettings)
    mock_page = MagicMock()
    mock_context = MagicMock()
    mock_browser = MagicMock()
    mock_sign_in.return_value = (mock_browser, mock_context, mock_page)
    mock_get_receipts.return_value = ["receipt1", "receipt2"]

    # Act
    main(settings=mock_settings)

    # Assert
    mock_sign_in.assert_called_once()
    mock_get_receipts.assert_called_once()
    assert mock_parse_receipt.call_count == 2
    mock_parse_receipt.assert_any_call(mock_page, "https://www.qfc.com/mypurchases/image/", "receipt1", "order_data.json")
    mock_parse_receipt.assert_any_call(mock_page, "https://www.qfc.com/mypurchases/image/", "receipt2", "order_data.json")
    mock_context.close.assert_called_once()
    mock_browser.close.assert_called_once()
