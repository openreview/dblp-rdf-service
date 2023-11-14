import structlog

def create_logger(logname: str):
    logger = structlog.get_logger(logname)
    return logger

