from typing import Optional, Union, TypeVar, Tuple, Dict, List
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


K = TypeVar('K')
V = TypeVar('V')


def pairs_to_multimap(kv_pairs: List[Tuple[K, V]]) -> Dict[K, List[V]]:
    mmap: Dict[K, List[V]] = {}
    for key, val in kv_pairs:
        mmap.setdefault(key, []).append(val)

    return mmap
