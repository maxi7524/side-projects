"""Behavioral checks for deterministic, atomic assignment data retrieval."""

import hashlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from _support.downloads import contained, prepare_provider, retrieve


class DownloadTests(unittest.TestCase):
    """Verify checksum, cache, containment, and retrieval behavior."""

    def setUp(self):
        """Create a deterministic isolated project and archive."""
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.project = self.root / "project"
        self.archive = self.root / "archive"
        self.project.mkdir()
        self.archive.mkdir()
        self.payload = b"feature,target\n1,2\n3,4\n"
        self.resource = {
            "path": "data/sample.csv",
            "sha256": hashlib.sha256(self.payload).hexdigest(),
            "archive_path": "source/sample.csv",
        }

    def test_archive_restoration_and_cache_avoid_network(self):
        """Restored bytes match the source and repeated retrieval performs no I/O."""
        source = self.archive / self.resource["archive_path"]
        source.parent.mkdir()
        source.write_bytes(self.payload)
        self.assertEqual(retrieve(self.resource, self.project, self.archive), "archive")
        self.assertEqual(
            (self.project / self.resource["path"]).read_bytes(), self.payload
        )
        source.unlink()
        with patch(
            "_support.downloads.urllib.request.urlopen",
            side_effect=AssertionError("Unexpected network"),
        ):
            self.assertEqual(
                retrieve(self.resource, self.project, self.archive), "cached"
            )

    def test_bad_checksum_preserves_existing_file(self):
        """Failed verification never replaces an existing input."""
        destination = self.project / self.resource["path"]
        destination.parent.mkdir()
        destination.write_bytes(b"existing bytes")
        self.resource["url"] = "https://example.test/sample.csv"
        with patch(
            "_support.downloads.urllib.request.urlopen",
            return_value=io.BytesIO(b"wrong bytes"),
        ):
            with self.assertRaises(RuntimeError):
                retrieve(self.resource, self.project)
        self.assertEqual(destination.read_bytes(), b"existing bytes")
        self.assertEqual(list(destination.parent.iterdir()), [destination])

    def test_http_retrieval_verifies_bytes(self):
        """A successful response is written into the assignment's data directory."""
        self.resource["url"] = "https://example.test/sample.csv"
        with patch(
            "_support.downloads.urllib.request.urlopen",
            return_value=io.BytesIO(self.payload),
        ):
            self.assertEqual(retrieve(self.resource, self.project), "url")
        self.assertEqual(
            (self.project / self.resource["path"]).read_bytes(), self.payload
        )

    def test_github_fallback_does_not_expose_credentials(self):
        """The GitHub client receives only a source endpoint and writes raw bytes."""
        self.resource["github_api"] = "repos/owner/repo/contents/sample.csv?ref=commit"

        def run(command, *, stdout, stderr, check):
            self.assertEqual(command[0:2], ["gh", "api"])
            self.assertNotIn("Authorization", " ".join(command))
            stdout.write(self.payload)

        with patch("_support.downloads.subprocess.run", side_effect=run):
            self.assertEqual(retrieve(self.resource, self.project), "github")

    def test_path_escape_rejected(self):
        """Traversal, absolute paths, and symlink escapes are outside the domain."""
        for relative in ["../escaped", "/tmp/escaped", "."]:
            with self.subTest(relative=relative), self.assertRaises(ValueError):
                contained(self.project, relative)
        (self.project / "link").symlink_to(self.archive, target_is_directory=True)
        with self.assertRaises(ValueError):
            contained(self.project, "link/escaped.csv")

    def test_missing_source_fails_without_empty_destination(self):
        """Unavailable resources cannot silently appear successfully prepared."""
        with self.assertRaises(RuntimeError):
            retrieve(self.resource, self.project, self.archive)
        self.assertFalse((self.project / self.resource["path"]).exists())

    def test_html_response_is_rejected(self):
        """Authentication pages must never masquerade as downloaded data."""
        self.resource["url"] = "https://example.test/confirmation"
        response = io.BytesIO(b"<html>confirmation required</html>")
        response.headers = {"Content-Type": "text/html"}
        with patch("_support.downloads.urllib.request.urlopen", return_value=response):
            with self.assertRaises(RuntimeError):
                retrieve(self.resource, self.project)
        self.assertFalse((self.project / self.resource["path"]).exists())

    def test_provider_reuses_existing_project_downloader(self):
        """The PDB provider invokes the retained script in its assignment."""
        provider = {"kind": "pdb", "path": "data/pdb", "script": "scripts/download.py"}
        with patch("_support.downloads.subprocess.run") as run:
            prepare_provider(provider, self.project)
        self.assertEqual(run.call_args.kwargs["cwd"], self.project)
        self.assertEqual(
            Path(run.call_args.args[0][1]), self.project / provider["script"]
        )

    def test_unknown_or_escaping_provider_is_rejected(self):
        """Providers obey the same path boundary as downloaded resources."""
        for provider in [
            {"kind": "unknown", "path": "data"},
            {"kind": "mnist", "path": "../data"},
        ]:
            with self.subTest(provider=provider), self.assertRaises(ValueError):
                prepare_provider(provider, self.project)


if __name__ == "__main__":
    unittest.main()
