import os

from typing import Final, Optional

DEFAULT_API_URL = "https://ripe.knukro.com/api"
DEFAULT_CONFIG_PATH = "config.json"


class Config:

    def __init__(self) -> None:
        self.base_url: Final[str] = os.environ.get("BASE_URL") or DEFAULT_API_URL
        self.device_config_path: Final[str] = (
            os.environ.get("CONFIG_PATH") or DEFAULT_CONFIG_PATH
        )
        self.rollback_cmd: Final[Optional[str]] = os.environ.get(
            "RIPE_LOOP_ROLLBACK_CMD"
        )


CONFIG = Config()
