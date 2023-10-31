import logging


def create_logger(logname: str):
    if '/' in logname:
        logname = logname.split('/')[-1]

    if '.' in logname:
        logname = logname.split('.')[0]

    logger = logging.getLogger(f"{logname}")
    logger.setLevel(logging.INFO)
    return logger
