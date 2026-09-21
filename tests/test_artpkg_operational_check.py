import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).parents[1] / "tools"))

import artpkg_operational_check as operational


class OperationalCheckTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.credentials = self.root / "credentials.json"
        self.credentials.write_text(json.dumps({"tester1": "secret1"}), encoding="utf-8")
        self.fixture = self.root / "probe.md"
        self.fixture.write_text("# Pre-Artifacts Package\n", encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def _args(self) -> list[str]:
        return [
            "--credentials-file", str(self.credentials),
            "--fixture", str(self.fixture),
            "--json",
        ]

    def test_deep_check_passes_with_optional_visual_check_warning(self):
        responses = [
            (200, {"Content-Type": "application/json"}, json.dumps(operational.EXPECTED_STATUS).encode()),
            (200, {"Content-Type": "text/html"}, b"viewer"),
            (401, {"WWW-Authenticate": 'Basic realm="ArtPkg Intake"'}, b""),
            (200, {"Content-Type": "text/html"}, b"<html>ArtPkg</html>"),
            (200, {"Content-Type": "application/json"}, json.dumps({"session_id": "probe", "session_dir": "/tmp/probe"}).encode()),
            (200, {"Content-Type": "application/json"}, json.dumps({
                "projection": {
                    "ready": True,
                    "error": None,
                    "archify": {
                        "validate": {"ok": True},
                        "deliver": {"ok": True},
                        "visual_check": {"ok": False, "receipt": {"error": "Chrome unavailable"}},
                    },
                }
            }).encode()),
            (200, {"Content-Type": "text/html; charset=utf-8"}, b"<html>" + b"x" * 1200 + b"</html>"),
        ]
        output = io.StringIO()

        with patch("artpkg_operational_check._request", side_effect=responses), redirect_stdout(output):
            exit_code = operational.main(self._args())

        report = json.loads(output.getvalue())
        self.assertEqual(0, exit_code)
        self.assertTrue(report["ok"])
        self.assertEqual("WARN", next(item["status"] for item in report["checks"] if item["name"] == "projection-visual-check"))
        self.assertEqual("PASS", next(item["status"] for item in report["checks"] if item["name"] == "projection-html"))

    def test_projection_delivery_failure_is_actionable_and_returns_nonzero(self):
        responses = [
            (200, {}, json.dumps(operational.EXPECTED_STATUS).encode()),
            (200, {}, b"viewer"),
            (401, {"WWW-Authenticate": "Basic realm=ArtPkg"}, b""),
            (200, {}, b"ArtPkg"),
            (200, {}, json.dumps({"session_id": "probe", "session_dir": "/tmp/probe"}).encode()),
            (200, {}, json.dumps({
                "projection": {
                    "ready": False,
                    "error": "Archify is not configured. Set ARTPKG_ARCHIFY_ROOT.",
                    "archify": {},
                }
            }).encode()),
        ]
        output = io.StringIO()

        with patch("artpkg_operational_check._request", side_effect=responses), redirect_stdout(output):
            exit_code = operational.main(self._args())

        report = json.loads(output.getvalue())
        failure = next(item for item in report["checks"] if item["name"] == "projection-generation")
        self.assertEqual(1, exit_code)
        self.assertFalse(report["ok"])
        self.assertEqual("FAIL", failure["status"])
        self.assertIn("ARTPKG_ARCHIFY_ROOT", failure["detail"])

    def test_shallow_mode_does_not_create_probe_session(self):
        responses = [
            (200, {}, json.dumps(operational.EXPECTED_STATUS).encode()),
            (200, {}, b"viewer"),
            (401, {"WWW-Authenticate": "Basic realm=ArtPkg"}, b""),
            (200, {}, b"ArtPkg"),
        ]
        output = io.StringIO()

        with patch("artpkg_operational_check._request", side_effect=responses) as request, redirect_stdout(output):
            exit_code = operational.main(["--credentials-file", str(self.credentials), "--shallow", "--json"])

        self.assertEqual(0, exit_code)
        self.assertEqual(4, request.call_count)
        self.assertNotIn("intake-workflow", output.getvalue())


if __name__ == "__main__":
    unittest.main()
