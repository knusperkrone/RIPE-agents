import os

from typing import Final, Optional

DEFAULT_API_URL = 'https://ripe.knukro.com/api'
DEFAULT_CONFIG_PATH = 'config.json'

class Config:

    def __init__(self) -> None:
        self.base_url: Final[str] = os.environ.get('BASE_URL')
        if self.base_url is None:
            self.base_url = DEFAULT_API_URL

        self.device_config_path: Final[str] = os.environ.get('CONFIG_PATH')
        if self.device_config_path is None:
            self.device_config_path = DEFAULT_CONFIG_PATH

        self.rollback_cmd: Final[Optional[str]] = os.environ.get('RIPE_LOOP_ROLLBACK_CMD')

CONFIG = Config()
