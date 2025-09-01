import logging
import os
from pydantic_settings import BaseSettings
from pydantic import SecretStr, StrictStr, model_validator 

"""Application settings using Pydantic BaseSettings."""


"""Initialize logging configuration."""
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
    LOGLEVEL: StrictStr = "INFO"
    KROGER_USERNAME: StrictStr
    KROGER_PASSWORD: SecretStr
    HEADLESS: bool = False


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
