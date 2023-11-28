from typing import Optional, Union
from email_validator import validate_email, EmailNotValidError


def is_valid_email(s: str) -> bool:
    try:
        validate_email(s).email
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
