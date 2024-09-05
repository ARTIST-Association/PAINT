import os

PAINT_ROOT = f"{os.sep}".join(__file__.split(os.sep)[:-2])
"""Reference to the root directory of ARTIST."""

__all__ = ["PAINT_ROOT", "data", "util"]
