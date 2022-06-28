import logging
import sys


def get_logger():

    logger = logging.getLogger(__name__)
    formatter = logging.Formatter('%(asctime)s - %(threadName)s - %(module)s:%(lineno)d - %(levelname)s - %(message)s')
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        # fileHandler = logging.FileHandler("logfile.log")
        # fileHandler.setFormatter(formatter)
        # logger.addHandler(fileHandler)
        
    return logger
