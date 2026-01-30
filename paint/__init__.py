import os
from importlib.metadata import PackageNotFoundError, version

PAINT_ROOT = f"{os.sep}".join(__file__.split(os.sep)[:-2])
"""Reference to the root directory of ARTIST."""
try:
    __version__ = version("paint-csp")
except PackageNotFoundError:
    # Allows running from source without installation.
    __version__ = "0.0.0"

__all__ = ["PAINT_ROOT", "preprocessing", "util", "__version__"]
