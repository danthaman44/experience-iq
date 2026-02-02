import logging

# Configure the logging module to output INFO messages (and higher) to the console
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def log_info(message: str):
    logging.info(message)


def log_error(message: str):
    logging.error(message)


def log_warning(message: str):
    logging.warning(message)


def log_debug(message: str):
    logging.debug(message)
