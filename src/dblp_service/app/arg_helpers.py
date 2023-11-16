import typing as t

def zero_or_one(strs: t.Tuple[str]) -> t.Tuple[bool, t.Optional[str]]:
    if len(strs) > 1:
        print("Too many arguments: only 0 or 1 allowed")
        return False, None

    if len(strs) == 1:
        return True, strs[0]

    return True, None
