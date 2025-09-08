from unittest.mock import MagicMock, patch
from unittest.mock import call

from app_settings import AppSettings
from main import main


@patch("main.parse_receipt")
@patch("main.get_receipts")
@patch("main.sign_in")
@patch("main.sync_playwright")
def test_main_happy_path(_mock_sync_playwright, mock_sign_in, mock_get_receipts, mock_parse_receipt):
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
    base_url = "https://www.qfc.com/mypurchases/image/"
    order_data_file = "order_data.json"
    expected_calls = [
        call(mock_page, base_url + "receipt1", "receipt1", order_data_file),
        call(mock_page, base_url + "receipt2", "receipt2", order_data_file),
    ]
    mock_parse_receipt.assert_has_calls(expected_calls, any_order=True)
    mock_context.close.assert_called_once()
    mock_browser.close.assert_called_once()
