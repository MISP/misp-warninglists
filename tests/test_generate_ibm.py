import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


TOOLS_DIR = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS_DIR))
SPEC = importlib.util.spec_from_file_location(
    "generate_ibm", TOOLS_DIR / "generate-ibm.py"
)
generate_ibm = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(generate_ibm)


class MainTest(unittest.TestCase):
    def test_dormant_asn_is_not_sent_to_holder_verification(self):
        prefixes = {
            36351: ["192.0.2.0/24"],
            46703: [],
        }

        with patch.object(generate_ibm, "IBM_CLOUD_ASNS", list(prefixes)), patch.object(
            generate_ibm,
            "get_networks_for_asn",
            side_effect=lambda asn: prefixes[asn],
        ), patch.object(generate_ibm, "verify_holder") as verify_holder, patch.object(
            generate_ibm, "sleep"
        ), patch.object(generate_ibm, "write_to_file") as write_to_file:
            generate_ibm.main()

        verify_holder.assert_called_once_with(36351)
        self.assertEqual(write_to_file.call_args.args[0]["list"], ["192.0.2.0/24"])


if __name__ == "__main__":
    unittest.main()
