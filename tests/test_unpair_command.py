"""Unit tests for the pybridge CLI unpair command."""

from __future__ import annotations

import contextlib
import io
import json
import unittest
from unittest.mock import AsyncMock, patch

from pybridge import cli


class FakeConfig:
    def __init__(self):
        self.identifier = "device-identifier"
        self.name = "Living Room"
        self.address = "10.0.0.10"
        self.all_identifiers = [self.identifier]


class FakeSettings:
    class Protocols:
        def __init__(self):
            self.airplay = type("AirPlay", (), {"credentials": "token", "password": None})()
            self.companion = type("Companion", (), {"credentials": "token"})()
            self.raop = type("Raop", (), {"credentials": None, "password": None})()
            self.mrp = type("Mrp", (), {"credentials": None})()
            self.dmap = type("Dmap", (), {"credentials": None})()

    def __init__(self):
        self.protocols = FakeSettings.Protocols()


def _patch_unpair_dependencies(removes_credentials: bool):
    settings = FakeSettings()

    # Companion credentials only exist in scenarios where they should be removed.
    settings.protocols.companion.credentials = "token" if removes_credentials else None

    async def get_settings(_config):
        return settings

    async def remove_credentials(_settings, _protocol):
        if removes_credentials:
            settings.protocols.companion.credentials = None
            return True
        return False

    storage_mock = AsyncMock()
    storage_mock.get_settings = AsyncMock(side_effect=get_settings)
    storage_mock.save = AsyncMock()

    patches = [
        patch("pybridge.pairing.load_storage", AsyncMock(return_value=storage_mock)),
        patch("pybridge.pairing.scan_configs", AsyncMock(return_value=[FakeConfig()])),
    ]

    return patches, storage_mock, settings


class UnpairCommandTests(unittest.TestCase):
    def test_unpair_success(self) -> None:
        patches, storage, settings = _patch_unpair_dependencies(removes_credentials=True)

        with contextlib.ExitStack() as stack:
            for item in patches:
                stack.enter_context(item)

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = cli.main(
                    [
                        "unpair",
                        "--identifier",
                        "device-identifier",
                        "--protocol",
                        "Companion",
                    ]
                )

        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertTrue(payload["credentials_removed"])
        storage.save.assert_awaited()
        self.assertIsNone(settings.protocols.companion.credentials)

    def test_unpair_no_credentials(self) -> None:
        patches, storage, _ = _patch_unpair_dependencies(removes_credentials=False)

        with contextlib.ExitStack() as stack:
            for item in patches:
                stack.enter_context(item)

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = cli.main(
                    [
                        "unpair",
                        "--identifier",
                        "device-identifier",
                        "--protocol",
                        "Companion",
                    ]
                )

        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertFalse(payload["credentials_removed"])
        storage.save.assert_not_awaited()


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
