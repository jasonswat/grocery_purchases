import unittest.mock as mock
from unittest.mock import MagicMock, patch

from utils import rotate_user_agent, setup_context, move_mouse


def test_rotate_user_agent():
    """Test that rotate_user_agent returns a random user agent string."""
    with patch("utils.UserAgent") as mock_user_agent:
        mock_instance = mock_user_agent.return_value
        mock_instance.random = "test_user_agent"
        result = rotate_user_agent()
        assert result == "test_user_agent"
        mock_user_agent.assert_called_once_with(os="Mac OS X")


@patch("utils.rotate_user_agent")
def test_setup_context(mock_rotate_user_agent):
    """Test that setup_context creates a browser and context with the correct parameters."""
    mock_playwright = MagicMock()
    mock_browser = MagicMock()
    mock_context = MagicMock()
    mock_playwright.chromium.launch.return_value = mock_browser
    mock_browser.new_context.return_value = mock_context
    mock_rotate_user_agent.return_value = "test_user_agent"

    mock_settings = MagicMock()
    mock_settings.HEADLESS = True

    browser, context = setup_context(mock_playwright, mock_settings)

    assert browser == mock_browser
    assert context == mock_context
    mock_playwright.chromium.launch.assert_called_once()
    mock_browser.new_context.assert_called_once_with(
        viewport={"width": 1280, "height": 720}, user_agent="test_user_agent"
    )
    mock_rotate_user_agent.assert_called_once()


@patch("utils.randint")
def test_move_mouse(mock_randint):
    """Test that move_mouse calls the correct mouse methods."""
    mock_page = MagicMock()
    mock_randint.return_value = 50

    move_mouse(mock_page)

    expected_calls = [
        mock.call.mouse.move(50, 50),
        mock.call.mouse.down(),
        mock.call.mouse.move(50, 150),
        mock.call.mouse.move(150, 150),
        mock.call.mouse.move(150, 50),
        mock.call.mouse.move(50, 50),
        mock.call.mouse.up(),
    ]
    assert mock_page.mock_calls == expected_calls
