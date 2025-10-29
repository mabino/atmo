"""Unit tests for the pybridge clear-storage command."""

from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from pybridge import cli


class ClearStorageCommandTests(unittest.TestCase):
    """Verify clearing stored credentials via the CLI."""

    def test_clear_storage_removes_existing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "settings.conf"
            storage_path.write_text("{}\n", encoding="utf-8")

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = cli.main(["--storage", str(storage_path), "clear-storage"])

        self.assertEqual(exit_code, 0)
        data = json.loads(stdout.getvalue())
        self.assertEqual(data["status"], "cleared")
        self.assertTrue(data["cleared"])
        self.assertFalse(storage_path.exists())

    def test_clear_storage_when_missing_is_noop(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "missing.conf"

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = cli.main(["--storage", str(storage_path), "clear-storage"])

        self.assertEqual(exit_code, 0)
        data = json.loads(stdout.getvalue())
        self.assertEqual(data["status"], "missing")
        self.assertFalse(data["cleared"])

    def test_mock_clear_storage_returns_mock_payload(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = cli.main(["--mock", "clear-storage"])

        self.assertEqual(exit_code, 0)
        data = json.loads(stdout.getvalue())
        self.assertEqual(data["status"], "cleared")
        self.assertTrue(data["cleared"])
        self.assertEqual(data["path"], "mock-storage")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
