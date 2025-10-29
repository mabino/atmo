"""Helpers for working with pyatv storage backends."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import os

from pyatv.interface import Storage
from pyatv.storage.file_storage import FileStorage


class StorageError(Exception):
    """Errors raised when creating or loading storage instances."""


@dataclass
class ClearStorageResult:
    """Result payload returned when clearing stored credentials."""

    status: str
    cleared: bool
    path: str


async def load_storage(
    loop: asyncio.AbstractEventLoop, path: Optional[str] = None
) -> Storage:
    """Create and load a storage backend.

    Args:
        loop: Active asyncio loop.
        path: Optional explicit path. When omitted, the pyatv default storage
            location is used (e.g. ``$HOME/.pyatv.conf``).

    Returns:
        A loaded ``Storage`` instance ready to be used with pyatv APIs.

    Raises:
        StorageError: If storage cannot be created or loaded.
    """

    try:
        storage = FileStorage(path, loop) if path else FileStorage.default_storage(loop)
        await storage.load()
    except Exception as exc:  # noqa: BLE001 - surface as StorageError
        raise StorageError("unable to initialize pyatv storage") from exc

    return storage


async def clear_storage(
    loop: asyncio.AbstractEventLoop, path: Optional[str] = None
) -> ClearStorageResult:
    """Remove persisted pyatv credentials from storage.

    The default location is ``$HOME/.pyatv.conf`` when *path* is omitted.
    """

    target = Path(path) if path else Path.home() / ".pyatv.conf"

    def _remove_file() -> bool:
        try:
            os.remove(target)
            return True
        except FileNotFoundError:
            return False

    try:
        removed = await loop.run_in_executor(None, _remove_file)
    except Exception as exc:  # noqa: BLE001 - surface as StorageError
        raise StorageError("unable to clear stored credentials") from exc

    status = "cleared" if removed else "missing"
    return ClearStorageResult(status=status, cleared=removed, path=target.as_posix())
