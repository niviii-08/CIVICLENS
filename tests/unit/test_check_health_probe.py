"""
CIVICLENS TN — Phase 12.7 Deployment Health Check Probe Tests
Validates the cross-platform check_health.py utility against mock and Flask endpoints.
"""

import json
import unittest
from unittest.mock import patch, MagicMock
import urllib.error

from scripts.check_health import probe_endpoint, main


class TestDeploymentHealthProbe(unittest.TestCase):
    """Test suite verifying deployment health probe behaviors."""

    @patch("urllib.request.urlopen")
    def test_probe_endpoint_success(self, mock_urlopen):
        """Verifies successful probe returns HTTP 200, parsed body, and duration."""
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps({"status": "healthy", "check": "liveness"}).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        status, payload, latency = probe_endpoint("http://localhost:5000/health/live")

        self.assertEqual(status, 200)
        self.assertEqual(payload.get("status"), "healthy")
        self.assertGreaterEqual(latency, 0.0)

    @patch("urllib.request.urlopen")
    def test_probe_endpoint_http_error(self, mock_urlopen):
        """Verifies probe handles HTTP 503 error payloads gracefully."""
        error_body = json.dumps({"status": "unhealthy", "database": "unavailable"}).encode("utf-8")
        fp_mock = MagicMock()
        fp_mock.read.return_value = error_body
        http_error = urllib.error.HTTPError(
            url="http://localhost:5000/health/ready",
            code=503,
            msg="Service Unavailable",
            hdrs={},
            fp=fp_mock
        )
        mock_urlopen.side_effect = http_error

        status, payload, latency = probe_endpoint("http://localhost:5000/health/ready")

        self.assertEqual(status, 503)
        self.assertEqual(payload.get("status"), "unhealthy")
        self.assertEqual(payload.get("database"), "unavailable")

    @patch("urllib.request.urlopen")
    def test_probe_endpoint_connection_refused(self, mock_urlopen):
        """Verifies probe returns status 0 and error details on network disconnect."""
        mock_urlopen.side_effect = urllib.error.URLError("Connection refused")

        status, payload, latency = probe_endpoint("http://127.0.0.1:9999/health")

        self.assertEqual(status, 0)
        self.assertIn("Connection refused", payload.get("error", ""))

    @patch("scripts.check_health.probe_endpoint")
    def test_main_success_exit_code(self, mock_probe):
        """Verifies main() exits with code 0 when both liveness and readiness pass."""
        mock_probe.side_effect = [
            (200, {"status": "healthy"}, 5.0),
            (200, {"status": "ready", "database": "connected"}, 8.0)
        ]

        with patch("sys.argv", ["check_health.py", "--url", "http://127.0.0.1:5000"]):
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 0)

    @patch("scripts.check_health.probe_endpoint")
    def test_main_failure_exit_code_on_unready_db(self, mock_probe):
        """Verifies main() exits with code 1 when database readiness fails."""
        mock_probe.side_effect = [
            (200, {"status": "healthy"}, 5.0),
            (503, {"status": "unhealthy", "database": "unavailable"}, 12.0)
        ]

        with patch("sys.argv", ["check_health.py", "--url", "http://127.0.0.1:5000"]):
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
