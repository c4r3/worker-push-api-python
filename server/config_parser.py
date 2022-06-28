import configparser
from typing import Optional

from server.backend_logger import get_logger


class ConfigurationParser:

    logger = get_logger()

    def __init__(self, path: str):
        self.logger.debug("Configuration at path %s", path)
        self.path = path
        self.config = configparser.ConfigParser()
        self.config.read(self.path)
        self.logger.debug("Configuration sections: %s", self.config.sections())

    def server_port(self) -> Optional[int]:
        return int(self.config['server']['port'])

    def monitoring_port(self) -> Optional[int]:
        return int(self.config['server']['port_monitoring'])

    def log_file_pat(self) -> str:
        return self.config['logging']['file_path']

    def bucket_size(self) -> Optional[int]:
        return int(self.config['server']['bucket_size'])

    def bucket_timeout(self) -> Optional[int]:
        return int(self.config['server']['bucket_timeout'])

    def shutdown_timeout(self) -> Optional[int]:
        return int(self.config['server']['shutdown_timeout'])
