import logging


class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    green = "\033[92m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    formats = "[%(asctime)s] %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + formats + reset,
        logging.INFO: green + formats + reset,
        logging.WARNING: yellow + formats + reset,
        logging.ERROR: red + formats + reset,
        logging.CRITICAL: bold_red + formats + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


logger = logging.getLogger("RIPE")
logger.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(CustomFormatter())

logger.addHandler(ch)
