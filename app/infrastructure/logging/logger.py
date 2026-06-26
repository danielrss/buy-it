import logging

# create logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# create console handler if not already added
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # add formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)
