import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, call, patch

import requests


TOOLS_DIR = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS_DIR))
SPEC = importlib.util.spec_from_file_location(
    "generate_akamai", TOOLS_DIR / "generate-akamai.py"
)
generate_akamai = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(generate_akamai)


class RipeStatTest(unittest.TestCase):
    def test_retries_connection_failure_with_backoff(self):
        response = Mock(status_code=200)
        response.json.return_value = {"data": "ok"}

        with patch.object(
            generate_akamai,
            "download",
            side_effect=[requests.ConnectionError("reset"), response],
        ), patch.object(generate_akamai, "sleep") as sleep:
            result = generate_akamai.ripestat("announced-prefixes", 20940)

        self.assertEqual(result, {"data": "ok"})
        self.assertEqual(sleep.call_args_list, [call(1.0), call(1), call(1.0)])

    def test_honours_retry_after_for_rate_limit(self):
        limited = Mock(status_code=429, headers={"Retry-After": "3"})
        response = Mock(status_code=200)
        response.json.return_value = {"data": "ok"}

        with patch.object(
            generate_akamai, "download", side_effect=[limited, response]
        ), patch.object(generate_akamai, "sleep") as sleep:
            generate_akamai.ripestat("abuse-contact-finder", 20940)

        self.assertEqual(sleep.call_args_list, [call(1.0), call(3.0), call(1.0)])

    def test_stops_after_bounded_number_of_failures(self):
        with patch.object(
            generate_akamai,
            "download",
            side_effect=requests.ConnectionError("reset"),
        ) as download, patch.object(generate_akamai, "sleep"):
            with self.assertRaisesRegex(RuntimeError, "after 5 attempts"):
                generate_akamai.ripestat("searchcomplete", "AKAMAI")

        self.assertEqual(download.call_count, 5)


if __name__ == "__main__":
    unittest.main()
