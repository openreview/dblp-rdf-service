import logging


def create_logger(logname: str):
    if '/' in logname:
        logname = logname.split('/')[-1]

    if '.' in logname:
        logname = logname.split('.')[0]

    logger = logging.getLogger(f"file:{logname}")
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(name)s [%(levelname)s] %(message)s")
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    ch.setLevel(logging.INFO)
    logger.addHandler(ch)
    return logger
