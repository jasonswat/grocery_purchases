import pytest
from unittest.mock import MagicMock, patch

from kroger import _perform_login


@pytest.fixture
def mock_settings():
    settings = MagicMock()
    settings.kroger_username = "testuser"
    settings.kroger_password.get_secret_value.return_value = "testpass"
    settings.max_sleep = 5
    settings.timeout = 1000
    return settings


@pytest.fixture
def mock_page():
    """Fixture for a mock Playwright page."""
    return MagicMock()


def test_perform_login(mock_page, mock_settings):
    """Tests the _perform_login function."""
    success_url = "https://example.com/success"

    _perform_login(mock_page, mock_settings, success_url)

    # Assert that the page interactions happened as expected
    mock_page.fill.assert_any_call("input#signInName", "testuser")
    mock_page.fill.assert_any_call("input#password", "testpass")
    mock_page.click.assert_called_once_with(
        "button#continue:not([disabled]):not([tabindex])"
    )
    mock_page.wait_for_url.assert_called_once_with(success_url, timeout=1000)


@patch("kroger.setup_context")
def test_sign_in(mock_setup_context, mock_settings):
    mock_playwright = MagicMock()
    mock_browser = MagicMock()
    mock_context = MagicMock()
    mock_page = MagicMock()
    mock_setup_context.return_value = (mock_browser, mock_context)
    mock_context.new_page.return_value = mock_page

    from kroger import sign_in

    browser, context, page = sign_in(
        mock_playwright, "https://example.com", mock_settings
    )

    assert browser == mock_browser
    assert context == mock_context
    assert page == mock_page
    mock_page.goto.assert_called_once_with("https://example.com", timeout=1000)


def test_get_receipt_html(mock_page, mock_settings):
    mock_page.inner_html.return_value = "<div>receipt</div>"

    from kroger import get_receipt_html

    html = get_receipt_html(mock_page, "https://example.com/receipt", mock_settings)

    assert html == "<div>receipt</div>"
    mock_page.goto.assert_called_once_with("https://example.com/receipt", timeout=1000)
    mock_page.wait_for_selector.assert_any_call("div.Receipt-container")


def test_ensure_signed_in_already_signed_in(mock_page, mock_settings):
    mock_page.wait_for_selector.side_effect = Exception("Not found")

    from kroger import ensure_signed_in

    ensure_signed_in(mock_page, mock_settings, "https://example.com")

    # Should not call _perform_login (which calls fill)
    assert mock_page.fill.call_count == 0
