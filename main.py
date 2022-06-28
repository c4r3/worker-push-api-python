import sys
import threading
import time

from prometheus_client import start_http_server

from server import config_parser
from server.backend_logger import get_logger
from server.config_parser import ConfigurationParser
from server.server import WorkerServer


if __name__ == '__main__':

    logger = get_logger()
    logger.info("*************************************")
    logger.info("*       Worker Push API Python      *")
    logger.info("*************************************")

    args = sys.argv[1:]
    if not args:
        logger.error("Invalid arguments")
        sys.exit(1)

    config: ConfigurationParser = config_parser.ConfigurationParser(args[0])

    start_http_server(config.monitoring_port())
    server = WorkerServer(config)
    threading.Thread(target=server.start, daemon=True, name="Server-Thread").start()
    logger.debug("Server thread started successfully")

    while not server.shutdown_completed:
        time.sleep(1.0)

    logger.info("Closing main thread, bye...")
