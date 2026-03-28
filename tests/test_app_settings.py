import logging
import os
import sys
from unittest.mock import patch

import pytest
from pydantic import SecretStr

from app_settings import AppSettings, get_log


@pytest.fixture(autouse=True)
def clear_env_vars(monkeypatch):
    """Clear environment variables used by AppSettings before each test."""
    app_settings_vars = [
        "LOGLEVEL",
        "KROGER_USERNAME",
        "KROGER_PASSWORD",
        "HEADLESS",
        "TIMEOUT",
        "MAX_SLEEP",
        "PAGES",
    ]
    for var in app_settings_vars:
        monkeypatch.delenv(var, raising=False)


def test_app_settings_pages(caplog):
    """Test that AppSettings correctly handles the pages setting."""
    base_env_vars = {
        "KROGER_USERNAME": "testuser",
        "KROGER_PASSWORD": "testpass",
    }

    # Test default
    with patch.dict(os.environ, base_env_vars):
        # We need to mock sys.argv to prevent CliSettingsSource from failing on pytest args
        with patch.object(sys, "argv", ["main.py"]):
            settings = AppSettings()
            assert settings.pages == "1"

    # Test specific page
    env_vars = base_env_vars.copy()
    env_vars["PAGES"] = "32"
    with patch.dict(os.environ, env_vars):
        with patch.object(sys, "argv", ["main.py"]):
            settings = AppSettings()
            assert settings.pages == "32"

    # Test all pages
    env_vars["PAGES"] = "all"
    with patch.dict(os.environ, env_vars):
        with patch.object(sys, "argv", ["main.py"]):
            settings = AppSettings()
            assert settings.pages == "all"

    # Test maxN pages
    env_vars["PAGES"] = "max10"
    with patch.dict(os.environ, env_vars):
        with patch.object(sys, "argv", ["main.py"]):
            settings = AppSettings()
            assert settings.pages == "max10"


def test_app_settings_cli_pages(caplog, monkeypatch):
    """Test that AppSettings correctly handles the pages setting via CLI."""
    monkeypatch.setenv("KROGER_USERNAME", "testuser")
    monkeypatch.setenv("KROGER_PASSWORD", "testpass")

    with patch.object(sys, "argv", ["main.py", "--pages", "42"]):
        settings = AppSettings()
        assert settings.pages == "42"


def test_get_log_default_level(caplog):
    """Test that the default log level is INFO."""
    logger = get_log()
    logger.info("test message")
    assert "test message" in caplog.text
    assert logger.level == logging.INFO


def test_get_log_custom_level(caplog):
    """Test that the log level can be set via environment variable."""
    with patch.dict(os.environ, {"LOGLEVEL": "DEBUG"}):
        logger = get_log()
        logger.debug("test message")
        assert "test message" in caplog.text
        assert logger.level == logging.DEBUG


def test_app_settings_loads_from_env(caplog):
    """Test that AppSettings loads configuration from environment variables."""
    env_vars = {
        "KROGER_USERNAME": "testuser",
        "KROGER_PASSWORD": "testpass",
        "HEADLESS": "true",
        "TIMEOUT": "30000",
        "MAX_SLEEP": "10",
    }
    with patch.dict(os.environ, env_vars):
        with patch.object(sys, "argv", ["main.py"]):
            with caplog.at_level(logging.INFO):
                settings = AppSettings()

                assert settings.kroger_username == "testuser"
                assert settings.kroger_password == SecretStr("testpass")
                assert settings.headless is True
                assert settings.timeout == 30000
                assert settings.max_sleep == 10

                # Check that the validator logged the settings
                assert "Application settings:" in caplog.text
                assert "kroger_username: testuser" in caplog.text
                assert "headless: True" in caplog.text
                assert "timeout: 30000" in caplog.text
                assert "max_sleep: 10" in caplog.text
                assert "testpass" not in caplog.text


def test_app_settings_missing_required_env_vars():
    """Test that AppSettings raises an error if required environment variables are missing."""
    with patch.object(sys, "argv", ["main.py"]):
        with pytest.raises(ValueError):
            AppSettings()
