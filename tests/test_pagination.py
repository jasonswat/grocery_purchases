import sys
import pytest
from unittest.mock import MagicMock, patch
from kroger import get_purchase_url, get_receipts


def test_get_purchase_url_https():
    base_url = "https://www.qfc.com/mypurchases"

    # Page 1 (default or explicit)
    assert (
        get_purchase_url(base_url, 1)
        == "https://www.qfc.com/mypurchases?tab=purchases&page=1"
    )
    assert (
        get_purchase_url(base_url, 42)
        == "https://www.qfc.com/mypurchases?tab=purchases&page=42"
    )


def test_get_purchase_url_file(tmp_path):
    # Mock local directory structure
    pagination_dir = tmp_path / "pagination"
    pagination_dir.mkdir()
    p1 = pagination_dir / "p1.html"
    p1.write_text("page 1")
    p2 = pagination_dir / "p2.html"
    p2.write_text("page 2")

    base_url = f"file://{pagination_dir}"

    assert get_purchase_url(base_url, 1) == f"file://{pagination_dir}/p1.html"
    assert get_purchase_url(base_url, 2) == f"file://{pagination_dir}/p2.html"

    # Should return None or raise error if file doesn't exist?
    # Spec says: "Scrapes all available pages until no more data is found."
    # So returning None seems appropriate for the loop to stop.
    assert get_purchase_url(base_url, 3) is None


@pytest.fixture
def mock_settings():
    settings = MagicMock()
    settings.max_sleep = 0
    settings.pages = "1"
    return settings


@patch("kroger.BeautifulSoup")
def test_get_receipts_single_page(mock_bs, mock_settings):
    mock_page = MagicMock()
    mock_settings.pages = "1"

    # Mock BS to return some items
    mock_soup = MagicMock()
    mock_bs.return_value = mock_soup
    mock_item = MagicMock()
    mock_a = MagicMock()
    mock_a.__getitem__.return_value = "/mypurchases/detail/receipt123"
    mock_item.find.return_value = mock_a
    mock_soup.select.return_value = [mock_item]

    receipts = get_receipts(mock_page, "https://example.com/mypurchases", mock_settings)

    assert receipts == ["receipt123"]
    # Should call goto twice: once for base, once for page 1
    assert mock_page.goto.call_count == 2
    mock_page.goto.assert_any_call(
        "https://example.com/mypurchases?tab=purchases&page=1"
    )


@patch("kroger.BeautifulSoup")
def test_get_receipts_max_pages(mock_bs, mock_settings):
    mock_page = MagicMock()
    mock_settings.pages = "max2"

    # Mock BS to return different items for different calls if needed
    # For simplicity, same item
    mock_soup = MagicMock()
    mock_bs.return_value = mock_soup
    mock_item = MagicMock()
    mock_a = MagicMock()
    mock_a.__getitem__.return_value = "/mypurchases/detail/receipt"
    mock_item.find.return_value = mock_a
    mock_soup.select.return_value = [mock_item]

    receipts = get_receipts(mock_page, "https://example.com/mypurchases", mock_settings)

    # max2 means page 1 and page 2
    assert len(receipts) == 2
    assert mock_page.goto.call_count == 3  # base + p1 + p2


def test_get_receipts_local_files(monkeypatch):
    # This test will use the actual files created in tests/html/pagination/
    # (assuming they were created in Phase 2)
    from pathlib import Path

    project_root = Path(__file__).parent.parent
    local_dir = project_root / "tests/html/pagination"

    if not local_dir.exists():
        pytest.skip("Local test directory not found. Phase 2 might have failed.")

    from playwright.sync_api import sync_playwright
    from app_settings import AppSettings
    from utils import setup_context

    monkeypatch.setenv("KROGER_USERNAME", "test")
    monkeypatch.setenv("KROGER_PASSWORD", "test")
    monkeypatch.setenv("PAGES", "max2")
    monkeypatch.setenv("HEADLESS", "true")

    with patch.object(sys, "argv", ["main.py"]):
        settings = AppSettings()

    with sync_playwright() as p:
        browser, context = setup_context(p, settings)
        page = context.new_page()

        # We use file:// prefix
        base_url = f"file://{local_dir.absolute()}"

        receipts = get_receipts(page, base_url, settings)

        # Each page (p1.html, p2.html) is a copy of mypurchases.html which has 10 receipts
        # So max2 should return 20 receipt IDs
        assert len(receipts) == 20

        # Test 'all'
        monkeypatch.setenv("PAGES", "all")
        with patch.object(sys, "argv", ["main.py"]):
            settings_all = AppSettings()
        receipts_all = get_receipts(page, base_url, settings_all)
        # Should stop after p2.html since p3.html doesn't exist
        assert len(receipts_all) == 20

        browser.close()


@patch("kroger.BeautifulSoup")
def test_get_receipts_invalid_pages(mock_bs, mock_settings):
    mock_page = MagicMock()
    mock_settings.pages = "invalid"

    mock_soup = MagicMock()
    mock_bs.return_value = mock_soup
    mock_item = MagicMock()
    mock_a = MagicMock()
    mock_a.__getitem__.return_value = "/mypurchases/detail/receipt"
    mock_item.find.return_value = mock_a
    mock_soup.select.return_value = [mock_item]

    receipts = get_receipts(mock_page, "https://example.com/mypurchases", mock_settings)

    # Should default to page 1
    assert len(receipts) == 1
    mock_page.goto.assert_any_call(
        "https://example.com/mypurchases?tab=purchases&page=1"
    )


def test_get_receipts_no_more_pages(mock_settings):
    mock_page = MagicMock()
    # Mock get_purchase_url to return None immediately for page 1
    with patch("kroger.get_purchase_url", return_value=None):
        receipts = get_receipts(
            mock_page, "https://example.com/mypurchases", mock_settings
        )
        assert receipts == []


def test_get_receipts_timeout_on_page(mock_settings):
    mock_page = MagicMock()
    mock_page.wait_for_selector.side_effect = Exception("Timeout")

    receipts = get_receipts(mock_page, "https://example.com/mypurchases", mock_settings)
    assert receipts == []


@patch("kroger.BeautifulSoup")
def test_get_receipts_target_pages_limit(mock_bs, mock_settings):
    mock_page = MagicMock()
    mock_settings.pages = "1"  # Only page 1

    mock_soup = MagicMock()
    mock_bs.return_value = mock_soup
    mock_item = MagicMock()
    mock_item.find.return_value = None
    mock_soup.select.return_value = [mock_item]

    receipts = get_receipts(mock_page, "https://example.com/mypurchases", mock_settings)
    assert len(receipts) == 0
    # Should stop after page 1
    assert mock_page.goto.call_count == 2


@patch("kroger.BeautifulSoup")
def test_get_receipts_specific_page_gt_1(mock_bs, mock_settings):
    mock_page = MagicMock()
    mock_settings.pages = "2"

    mock_soup = MagicMock()
    mock_bs.return_value = mock_soup
    mock_item = MagicMock()
    mock_a = MagicMock()
    mock_a.__getitem__.return_value = "/mypurchases/detail/receipt"
    mock_item.find.return_value = mock_a
    mock_soup.select.return_value = [mock_item]

    receipts = get_receipts(mock_page, "https://example.com/mypurchases", mock_settings)

    assert len(receipts) == 1
    # Should NOT call for page 1, only for page 2 (and base)
    assert mock_page.goto.call_count == 2
    mock_page.goto.assert_any_call(
        "https://example.com/mypurchases?tab=purchases&page=2"
    )
