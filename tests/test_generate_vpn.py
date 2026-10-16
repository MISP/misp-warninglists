import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import requests


TOOLS_DIR = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS_DIR))
SPEC = importlib.util.spec_from_file_location(
    "generate_vpn", TOOLS_DIR / "generate-vpn.py"
)
generate_vpn = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(generate_vpn)


class GenerateVpnTest(unittest.TestCase):
    def test_main_uses_separate_feeds_for_both_ip_versions(self):
        feeds = {
            "vpn/ipv4.txt": "# VPNs\n\n 192.0.2.0/25 \n192.0.2.128/25\n192.0.2.0/25\n",
            "vpn/ipv6.txt": "2001:db8::/48\n",
            "datacenter/ipv4.txt": "198.51.100.0/24\n",
            "datacenter/ipv6.txt": "2001:db8:1::/48\n",
        }

        def response_for(url):
            return Mock(text=feeds[url[len(generate_vpn.SOURCE) + 1:]])

        with patch.object(generate_vpn, "download", side_effect=response_for) as download, patch.object(
            generate_vpn, "write_to_file"
        ) as write:
            generate_vpn.main()

        self.assertEqual(
            [call.args[0] for call in download.call_args_list],
            [generate_vpn.SOURCE + "/" + path for path in feeds],
        )
        generated = {call.args[1]: call.args[0] for call in write.call_args_list}
        self.assertEqual(
            set(generated),
            {"vpn-ipv4", "vpn-ipv6", "datacenter-ipv4", "datacenter-ipv6"},
        )
        self.assertEqual(generated["vpn-ipv4"]["list"], ["192.0.2.0/24"])
        self.assertEqual(generated["vpn-ipv6"]["list"], ["2001:db8::/48"])
        self.assertEqual(generated["datacenter-ipv4"]["list"], ["198.51.100.0/24"])
        self.assertEqual(generated["datacenter-ipv6"]["list"], ["2001:db8:1::/48"])
        self.assertNotIn("datacenters", generated["vpn-ipv4"]["description"])
        self.assertIn(
            "datacenters and VPN providers", generated["datacenter-ipv4"]["description"]
        )
        for dst, warninglist in generated.items():
            self.assertEqual(warninglist["type"], "cidr")
            self.assertIn("ip-src", warninglist["matching_attributes"])
            self.assertIn(dst.replace("-", "/") + ".txt", warninglist["description"])

    def test_http_failure_does_not_write_a_list(self):
        response = Mock(text="192.0.2.0/24\n")
        response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        with patch.object(generate_vpn, "download", return_value=response), patch.object(
            generate_vpn, "write_to_file"
        ) as write:
            with self.assertRaises(requests.HTTPError):
                generate_vpn.process("vpn", 4)
        write.assert_not_called()

    def test_invalid_feeds_do_not_write_a_list(self):
        for text in ("# no networks\n\n", "not a network", "2001:db8::/32"):
            with self.subTest(text=text), patch.object(
                generate_vpn, "download", return_value=Mock(text=text)
            ), patch.object(generate_vpn, "write_to_file") as write:
                with self.assertRaises(ValueError):
                    generate_vpn.process("vpn", 4)
                write.assert_not_called()


if __name__ == "__main__":
    unittest.main()
