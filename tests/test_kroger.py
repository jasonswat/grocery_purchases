import pytest
from unittest.mock import MagicMock, patch

from kroger import _perform_login


@pytest.fixture
def mock_settings():
    settings = MagicMock()
    settings.KROGER_USERNAME = "testuser"
    settings.KROGER_PASSWORD.get_secret_value.return_value = "testpass"
    settings.MAX_SLEEP = 5
    settings.TIMEOUT = 1000
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
