import structlog
import typing as t

AppLogger: t.TypeAlias = structlog.stdlib.BoundLogger

def create_logger(logname: str) -> AppLogger:
    logger = structlog.stdlib.get_logger(logname)
    return logger

