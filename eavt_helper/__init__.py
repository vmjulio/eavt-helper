"""eavt-helper — convert snapshots ↔ EAVT logs ↔ SCD Type 2 tables."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("eavt-helper")
except PackageNotFoundError:
    # Package is not installed (e.g. running from a source checkout without
    # `pip install -e .`). Fall back to a sentinel.
    __version__ = "0.0.0+unknown"

__all__ = ["__version__"]
