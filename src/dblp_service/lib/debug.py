#!/usr/bin/env python3


def install_icecream():
    from icecream import install # type: ignore
    install()

# try:
#     install()
# except ImportError:  # Graceful fallback if IceCream isn't installed.
#     ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa
