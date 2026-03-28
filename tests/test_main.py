from unittest.mock import MagicMock, patch, call

from app_settings import AppSettings
from main import main


@patch("main.output_receipt")
@patch("main.parse_receipt")
@patch("main.get_receipts")
@patch("main.setup_context")  # Patch setup_context
@patch("playwright.sync_api.sync_playwright")  # Patch sync_playwright
def test_main_happy_path(
    mock_sync_playwright,
    mock_setup_context,  # New argument for the patched object
    mock_get_receipts,
    mock_parse_receipt,
    mock_output_receipt,
):
    """Test the main function in a happy path scenario."""
    # Arrange
    mock_settings = MagicMock(spec=AppSettings)
    mock_settings.headless = True
    mock_settings.pages = "1"
    mock_page = MagicMock()
    mock_context = MagicMock()
    mock_browser = MagicMock()

    # Configure the mock_sync_playwright
    mock_playwright_context = MagicMock()
    mock_playwright_context.__enter__.return_value.chromium.launch.return_value = (
        mock_browser
    )
    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page
    mock_sync_playwright.return_value = mock_playwright_context

    # Configure mock_setup_context to return mock_browser and mock_context
    mock_setup_context.return_value = (mock_browser, mock_context)

    mock_get_receipts.return_value = ["receipt1", "receipt2"]
    mock_receipt_info = {
        "receipt_id": "receipt1",
        "date": "2025-09-13",
        "total": "100.00",
        "tax": "10.00",
        "store_name": "QFC",
        "store_id": "00851",
        "order_type": "In-Store",
        "items": [],
    }
    mock_parse_receipt.return_value = mock_receipt_info

    # Act
    main(settings=mock_settings)

    # Assert
    mock_get_receipts.assert_called_once()
    base_url = "https://www.qfc.com/mypurchases/image/"
    expected_parse_calls = [
        call(mock_page, base_url + "receipt1", "receipt1"),
        call(mock_page, base_url + "receipt2", "receipt2"),
    ]
    mock_parse_receipt.assert_has_calls(expected_parse_calls, any_order=True)

    expected_output_calls = [
        call(mock_receipt_info, ""),
        call(mock_receipt_info, ""),
    ]
    mock_output_receipt.assert_has_calls(expected_output_calls, any_order=True)
    mock_context.close.assert_called_once()
    mock_browser.close.assert_called_once()


@patch("main.output_receipt")
@patch("main.parse_receipt")
@patch("main.get_receipts")
@patch("main.setup_context")
@patch("playwright.sync_api.sync_playwright")
def test_main_parse_error(
    mock_sync_playwright,
    mock_setup_context,
    mock_get_receipts,
    mock_parse_receipt,
    mock_output_receipt,
):
    """Test that main continues if one receipt fails to parse."""
    mock_settings = MagicMock(spec=AppSettings)
    mock_settings.headless = True
    mock_settings.pages = "1"
    mock_page = MagicMock()
    mock_context = MagicMock()
    mock_browser = MagicMock()

    mock_playwright_context = MagicMock()
    mock_playwright_context.__enter__.return_value.chromium.launch.return_value = (
        mock_browser
    )
    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page
    mock_sync_playwright.return_value = mock_playwright_context
    mock_setup_context.return_value = (mock_browser, mock_context)

    mock_get_receipts.return_value = ["fail", "success"]

    # First call raises error, second succeeds
    mock_parse_receipt.side_effect = [
        Exception("Parse error"),
        {"receipt_id": "success", "items": []},
    ]

    from main import main

    main(settings=mock_settings)

    assert mock_parse_receipt.call_count == 2
    mock_output_receipt.assert_called_once()  # Only for the successful one
