from typing import Generator, Optional, Union
from email_validator import validate_email, EmailNotValidError  # type: ignore


def nextnums(init: int = 0) -> Generator[int, None, None]:
    i = init
    while 1:
        yield i
        i = i + 1


def is_valid_email(s: str) -> bool:
    try:
        validate_email(s).email  # type: ignore
        return True
    except EmailNotValidError:
        return False

def to_int(value: Optional[Union[str, int]]) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, int):
        return value

    try:
        return int(value)
    except Exception:
        return None
