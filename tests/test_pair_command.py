"""Unit tests for the pybridge CLI pair command."""

from __future__ import annotations

import contextlib
import io
import json
import unittest
from unittest.mock import AsyncMock, patch

from pybridge import cli
from pybridge.pairing import DEFAULT_PIN


class FakeConfig:
    def __init__(self):
        self.identifier = "11223344-5566-7788-9900-112233445566"
        self.all_identifiers = [self.identifier, "00:11:22:33:44:55"]
        self.name = "Living Room"
        self.address = "10.0.0.10"


class FakeService:
    def __init__(self):
        self.credentials = None


class FakePairingHandler:
    def __init__(self, device_provides_pin: bool):
        self._device_provides_pin = device_provides_pin
        self.has_paired = False
        self.service = FakeService()
        self.begin_called = False
        self.finish_called = False
        self.close_called = False
        self.pin_value = None

    @property
    def device_provides_pin(self) -> bool:
        return self._device_provides_pin

    def pin(self, pin):
        self.pin_value = str(pin)

    async def begin(self):
        self.begin_called = True

    async def finish(self):
        self.finish_called = True
        if self.pin_value:
            self.has_paired = True
            self.service.credentials = f"cred-{self.pin_value}"

    async def close(self):
        self.close_called = True


class FakeStorage:
    def __init__(self):
        self.saved = False

    async def save(self):
        self.saved = True


class PairCommandTests(unittest.TestCase):
    """Tests covering the pair command output."""

    def _patch_pair_dependencies(self, handler: FakePairingHandler):
        storage = FakeStorage()
        patches = [
            patch("pybridge.pairing.load_storage", AsyncMock(return_value=storage)),
            patch(
                "pybridge.pairing.scan_configs",
                AsyncMock(return_value=[FakeConfig()]),
            ),
            patch("pybridge.pairing.pyatv_pair", AsyncMock(return_value=handler)),
        ]
        return patches, storage

    def test_pair_requires_pin(self) -> None:
        handler = FakePairingHandler(device_provides_pin=True)
        patches, storage = self._patch_pair_dependencies(handler)

        with contextlib.ExitStack() as stack:
            for item in patches:
                stack.enter_context(item)

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = cli.main(
                    [
                        "pair",
                        "--identifier",
                        "11223344-5566-7788-9900-112233445566",
                        "--protocol",
                        "Companion",
                    ]
                )

        self.assertEqual(exit_code, 0)
        data = json.loads(stdout.getvalue())
        self.assertEqual(data["status"], "pin_required")
        self.assertFalse(storage.saved)
        self.assertTrue(handler.close_called)
        self.assertFalse(handler.finish_called)

    def test_pair_with_pin_succeeds(self) -> None:
        handler = FakePairingHandler(device_provides_pin=True)
        patches, storage = self._patch_pair_dependencies(handler)

        with contextlib.ExitStack() as stack:
            for item in patches:
                stack.enter_context(item)

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = cli.main(
                    [
                        "pair",
                        "--identifier",
                        "Living Room",
                        "--protocol",
                        "Companion",
                        "--pin",
                        "4021",
                    ]
                )

        self.assertEqual(exit_code, 0)
        data = json.loads(stdout.getvalue())
        self.assertEqual(data["status"], "paired")
        self.assertTrue(storage.saved)
        self.assertTrue(handler.close_called)
        self.assertTrue(handler.finish_called)
        self.assertEqual(handler.pin_value, "4021")
        self.assertEqual(data["credentials"], "cred-4021")

    def test_pair_without_pin_uses_default_when_not_required(self) -> None:
        handler = FakePairingHandler(device_provides_pin=False)
        patches, storage = self._patch_pair_dependencies(handler)

        with contextlib.ExitStack() as stack:
            for item in patches:
                stack.enter_context(item)

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = cli.main(
                    [
                        "pair",
                        "--identifier",
                        "10.0.0.10",
                        "--protocol",
                        "RAOP",
                    ]
                )

        self.assertEqual(exit_code, 0)
        data = json.loads(stdout.getvalue())
        self.assertEqual(data["status"], "paired")
        self.assertTrue(storage.saved)
        self.assertEqual(handler.pin_value, DEFAULT_PIN)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
