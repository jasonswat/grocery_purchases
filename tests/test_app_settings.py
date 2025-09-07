import logging
import os
from unittest.mock import patch

import pytest
from pydantic import SecretStr

from app_settings import AppSettings, get_log


@pytest.fixture(autouse=True)
def clear_env_vars():
    """Clear environment variables before each test."""
    os.environ.clear()


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
        with caplog.at_level(logging.INFO):
            settings = AppSettings()

            assert settings.KROGER_USERNAME == "testuser"
            assert settings.KROGER_PASSWORD == SecretStr("testpass")
            assert settings.HEADLESS is True
            assert settings.TIMEOUT == 30000
            assert settings.MAX_SLEEP == 10

            # Check that the validator logged the settings
            assert "Application settings:" in caplog.text
            assert "KROGER_USERNAME: testuser" in caplog.text
            assert "HEADLESS: True" in caplog.text
            assert "TIMEOUT: 30000" in caplog.text
            assert "MAX_SLEEP: 10" in caplog.text
            assert "testpass" not in caplog.text


def test_app_settings_missing_required_env_vars():
    """Test that AppSettings raises an error if required environment variables are missing."""
    with pytest.raises(ValueError):
        AppSettings()
