import sys
import unittest
from pathlib import Path
from unittest.mock import patch


TOOLS_DIR = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS_DIR))
import generator  # noqa: E402


PUBLIC_SUFFIXES = {"com", "uk", "ac.uk", "github.io", "s3.amazonaws.com"}


class FilterHostnameEntriesTest(unittest.TestCase):
    def filter(self, entries, **kwargs):
        with patch.object(generator, "get_public_suffixes", return_value=PUBLIC_SUFFIXES):
            return generator.filter_hostname_entries(entries, **kwargs)

    def test_normalises_entries(self):
        self.assertEqual(
            self.filter([" Example.COM \n", ".example.org.", "marketingplatform.google...."]),
            ["example.com", "example.org", "marketingplatform.google"],
        )

    def test_drops_junk(self):
        self.assertEqual(
            self.filter(["domain", "web", '"com,example.com.host"', "-bad.example.com",
                         "has space.example.com", "example.com", "csv-junk.example.net"],
                        junk={"csv-junk.example.net"}),
            ["example.com"],
        )

    def test_drops_public_suffixes_and_their_parents(self):
        self.assertEqual(
            self.filter(["ac.uk", "ox.ac.uk", "github.io", "user.github.io", "amazonaws.com"]),
            ["ox.ac.uk", "user.github.io"],
        )

    def test_drops_too_wide(self):
        self.assertEqual(
            self.filter(["wordpress.com", "WordPress.com", "blog.wordpress.com", "example.com"],
                        too_wide={"wordpress.com"}),
            ["blog.wordpress.com", "example.com"],
        )

    def test_split_returns_the_too_wide_entries(self):
        with patch.object(generator, "get_public_suffixes", return_value=PUBLIC_SUFFIXES):
            kept, too_wide = generator.split_hostname_entries(
                ["Example.com", "github.io", "amazonaws.com", "WordPress.com", "domain"],
                too_wide={"wordpress.com"},
                junk={"domain"},
            )
        self.assertEqual(kept, ["example.com"])
        # Junk is not a domain, so it is not kept for exact matching either.
        self.assertEqual(too_wide, ["amazonaws.com", "github.io", "wordpress.com"])


class WriteExactMatchWarninglistTest(unittest.TestCase):
    def test_writes_a_string_list_without_url_matching(self):
        written = {}
        with patch.object(generator, "write_to_file",
                          side_effect=lambda warninglist, dst: written.update(warninglist=warninglist, dst=dst)):
            generator.write_exact_match_warninglist(
                ["windows.net", "github.io", "windows.net"], "example-exact", "Name", "Description")
        self.assertEqual(written["dst"], "example-exact")
        warninglist = written["warninglist"]
        # MISP matches a "string" list exactly: windows.net, not <account>.blob.core.windows.net.
        self.assertEqual(warninglist["type"], "string")
        self.assertEqual(warninglist["list"], ["github.io", "windows.net"])
        self.assertEqual(warninglist["matching_attributes"], ["hostname", "domain", "domain|ip"])


if __name__ == "__main__":
    unittest.main()
