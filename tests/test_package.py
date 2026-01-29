import importlib
import importlib.metadata
from importlib.metadata import PackageNotFoundError
from unittest.mock import MagicMock

import pytest

import paint


def test_version_fallback_when_package_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Verify that ``__version__`` falls back to '0.0.0' if the package is not installed.

    This test mocks ``importlib.metadata.version`` to raise ``PackageNotFoundError``,
    then reloads the module to trigger the except block.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        MonkeyPatch fixture.
    """
    # Create a mock that raises the specific error.
    mock_raiser = MagicMock(side_effect=PackageNotFoundError)

    # Apply the mock to the standard library function.
    monkeypatch.setattr(importlib.metadata, "version", mock_raiser)

    # Reload the module to force the top-level try/except block to run again.
    importlib.reload(paint)

    # Assert the fallback behavior.
    assert paint.__version__ == "0.0.0"
