from typing import NamedTuple


class Slice(NamedTuple):
    """Represent an interval (start, start+len)"""

    start: int
    length: int

    def end(self) -> int:
        return self.start + self.length

    def __str__(self) -> str:
        return f"slice({self.start}-{self.end()})"

    def __repr__(self) -> str:
        return str(self)

    def __format__(self, __format_spec: str) -> str:
        return format(str(self), __format_spec)
