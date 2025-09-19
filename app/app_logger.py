import logging

_log_format = f"%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
DEFAULT_LOG_FILE = "uniskad.log"
DEFAULT_LOG_LEVEL = "INFO"


def get_file_handler():
    file_handler = logging.FileHandler(DEFAULT_LOG_FILE)
    file_handler.setLevel(DEFAULT_LOG_LEVEL)
    file_handler.setFormatter(logging.Formatter(_log_format))
    return file_handler


def get_stream_handler():
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(DEFAULT_LOG_LEVEL)
    stream_handler.setFormatter(logging.Formatter(_log_format))
    return stream_handler


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(DEFAULT_LOG_LEVEL)
    logger.addHandler(get_file_handler())
    logger.addHandler(get_stream_handler())
    return logger
