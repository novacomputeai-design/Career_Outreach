"""No-network tests for the pinned HTTPS source witness and DNS-rebinding protection."""
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from outreach_agent.career_source_witness import (
    MAX_BYTES, _pinned_curl_command, bounded_fetch,
)

PUBLIC = lambda host, port, **k: [(2,1,0,"",("93.184.216.34",443))]
PRIVATE = lambda host, port, **k: [(2,1,0,"",("127.0.0.1",443))]
MIXED = lambda host, port, **k: [
    (2,1,0,"",("93.184.216.34",443)),
    (2,1,0,"",("10.1.2.3",443)),
]


class PinnedNetworkTests(unittest.TestCase):
    def test_actual_socket_is_pinned_to_public_resolved_address(self):
        commands = []
        def fake_run(argv, *, stdout, stderr, timeout, check):
            commands.append(argv)
            Path(argv[argv.index("--dump-header")+1]).write_bytes(
                b"HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n")
            stdout.write(b"<html><body>Verified test phrase</body></html>")
            return SimpleNamespace(returncode=0)
        text, content_type = bounded_fetch(
            "https://employer.example/strategy", resolver=PUBLIC,
            runner=fake_run, curl_path="mocked-curl")
        self.assertIn("Verified test phrase", text)
        self.assertEqual(content_type, "text/html")
        argv = commands[0]
        self.assertEqual(argv[argv.index("--resolve")+1],
                         "employer.example:443:93.184.216.34")
        self.assertEqual(argv[argv.index("--proto")+1], "=https")
        self.assertEqual(argv[argv.index("--noproxy")+1], "*")
        self.assertNotIn("--location", argv)
        self.assertNotIn("--insecure", argv)
        self.assertNotIn("-k", argv)

    def test_private_dns_is_rejected_before_transport(self):
        def fail(*args, **kwargs):
            raise AssertionError("Network transport must not be called")
        with self.assertRaises(ValueError):
            bounded_fetch("https://employer.example/strategy",
                          resolver=PRIVATE, runner=fail, curl_path="mocked-curl")
        with self.assertRaises(ValueError):
            bounded_fetch("https://employer.example/strategy",
                          resolver=MIXED, runner=fail, curl_path="mocked-curl")

    def test_nonpublic_ip_cannot_be_pinned(self):
        with self.assertRaises(ValueError):
            _pinned_curl_command(
                "https://employer.example", "127.0.0.1",
                "mocked-curl", "/tmp/headers")

    def test_redirect_is_not_considered_source_evidence(self):
        def fake_redirect(argv, *, stdout, stderr, timeout, check):
            Path(argv[argv.index("--dump-header")+1]).write_bytes(
                b"HTTP/1.1 302 Found\r\nLocation: http://127.0.0.1/\r\n\r\n")
            return SimpleNamespace(returncode=0)
        with self.assertRaises(ValueError):
            bounded_fetch("https://employer.example", resolver=PUBLIC,
                          runner=fake_redirect, curl_path="mocked-curl")

    def test_response_content_type_and_size_are_bounded(self):
        def huge(argv, *, stdout, stderr, timeout, check):
            Path(argv[argv.index("--dump-header")+1]).write_bytes(
                b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n")
            stdout.write(b"a"*(MAX_BYTES+1))
            return SimpleNamespace(returncode=0)
        with self.assertRaises(ValueError):
            bounded_fetch("https://employer.example", resolver=PUBLIC,
                          runner=huge, curl_path="mocked-curl")

    def test_missing_pinned_client_is_a_hold_not_fallback(self):
        with self.assertRaises(ValueError):
            bounded_fetch("https://127.0.0.1/private", resolver=PUBLIC,
                          curl_path="mocked-curl")

if __name__=="__main__":
    unittest.main()
