import logging
import os
import sys
from typing import Tuple, Type
from pydantic_settings import (
    BaseSettings,
    CliSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)
from pydantic import SecretStr, StrictStr, model_validator

"""Application settings using Pydantic BaseSettings."""


def get_log() -> logging.Logger:
    loglevel = os.getenv("LOGLEVEL", "INFO").upper()
    log = logging.getLogger("app")
    log.setLevel(loglevel)
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    if not log.handlers:
        log.addHandler(handler)
    return log


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(cli_parse_args=True)

    loglevel: StrictStr = "INFO"  # Default log level
    kroger_username: StrictStr  # Variable for Kroger, QFC, Fred Meyer username
    kroger_password: SecretStr  # Variable for Kroger, QFC, Fred Meyer password
    headless: bool = False  # Run browser in headless mode if True
    timeout: int = (
        60000  # Timeout for page loads in milliseconds, default is 60000 (60 seconds)
    )
    max_sleep: int = (
        20  # Maximum sleep time in seconds for simulating human interaction
    )
    pages: StrictStr = "1"  # Pages to scrape: "N", "all", or "maxN"

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
            CliSettingsSource(settings_cls, cli_parse_args=True),
        )

    @model_validator(mode="after")
    def log_settings_on_startup(self) -> "AppSettings":
        """
        Log the application settings on startup, excluding sensitive information.
        """
        log = get_log()
        settings_to_log = self.model_dump()

        log.info("Application settings:")
        for key, value in settings_to_log.items():
            log.info(f"{key}: {value}")

        return self
