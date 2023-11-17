import structlog
import typing as t

AppLogger: t.TypeAlias = structlog.BoundLogger

def create_logger(logname: str) -> AppLogger:
    logger = structlog.get_logger(logname)
    return logger
