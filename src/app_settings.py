import logging
import os
from pydantic_settings import BaseSettings
from pydantic import SecretStr, StrictStr, model_validator

"""Application settings using Pydantic BaseSettings."""


def get_log():
    loglevel = os.getenv('LOGLEVEL', 'INFO').upper()
    logging.basicConfig(
        level=loglevel,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    log = logging.getLogger(__name__)
    return log


log = get_log()


class AppSettings(BaseSettings):
    LOGLEVEL: StrictStr = "INFO"  # Default log level
    KROGER_USERNAME: StrictStr    # Variable for Kroger, QFC, Fred Meyer username
    KROGER_PASSWORD: SecretStr    # Variable for Kroger, QFC, Fred Meyer password
    HEADLESS: bool = False        # Run browser in headless mode if True
    TIMEOUT: int = 60000          # Timeout for page loads in milliseconds, default is 60000 (60 seconds)
    MAX_SLEEP: int = 20           # Maximum sleep time in seconds for simulating human interaction

    @model_validator(mode='after')
    def log_settings_on_startup(self) -> "AppSettings":
        """
        Log the application settings on startup, excluding sensitive information.
        """
        settings_to_log = self.model_dump()

        logging.info("Application settings:")
        for key, value in settings_to_log.items():
            logging.info(f"{key}: {value}")

        return self
