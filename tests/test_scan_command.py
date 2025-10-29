"""Unit tests for the pybridge CLI scan command."""

from __future__ import annotations

import io
import json
import contextlib
import unittest

from pybridge import cli


class ScanCommandTests(unittest.TestCase):
    """Verify the scan command behaviour."""

    def test_mock_scan_outputs_devices(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = cli.main(["--mock", "scan"])

        self.assertEqual(exit_code, 0)

        data = json.loads(stdout.getvalue())
        self.assertIn("devices", data)
        self.assertGreater(len(data["devices"]), 0)

        device = data["devices"][0]
        self.assertIn("name", device)
        self.assertIn("protocols", device)
        self.assertIsInstance(device["protocols"], list)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
