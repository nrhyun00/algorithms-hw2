import http.client
import os
import sys
import threading
import unittest
from urllib.parse import urlencode

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from server import TABLES, make_server


class ServerContract:
    table = "chaining"

    def setUp(self):
        self.server = make_server(port=0, table=self.table, host="127.0.0.1")
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()

    def request(self, method, path, body=None, headers=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        conn.request(method, path, body=body, headers=headers or {})
        resp = conn.getresponse()
        data = resp.read().decode("utf-8")
        conn.close()
        return resp, data

    def shorten(self, url, headers=None):
        h = {"Content-Type": "application/x-www-form-urlencoded"}
        h.update(headers or {})
        return self.request("POST", "/shorten", urlencode({"url": url}), h)

    def test_form(self):
        resp, body = self.request("GET", "/")
        self.assertEqual(resp.status, 200)
        self.assertIn("<form", body)

    def test_shorten_and_redirect(self):
        resp, body = self.shorten("https://example.com/hello")
        self.assertEqual(resp.status, 200)
        self.assertIn(f"127.0.0.1:{self.port}/1", body)
        resp, _ = self.request("GET", "/1")
        self.assertEqual(resp.status, 302)
        self.assertEqual(resp.getheader("Location"), "https://example.com/hello")

    def test_bad_url(self):
        resp, _ = self.shorten("ftp://example.com")
        self.assertEqual(resp.status, 400)

    def test_unknown_code(self):
        resp, body = self.request("GET", "/zzz")
        self.assertEqual(resp.status, 404)
        self.assertIn("href='/'", body)

    def test_forwarded_host(self):
        resp, body = self.shorten("https://example.com/a",
                                  {"X-Forwarded-Host": "abc-8000.app.github.dev"})
        self.assertIn("https://abc-8000.app.github.dev/1", body)
        self.assertNotIn("localhost", body)

    def test_table_page(self):
        self.shorten("https://example.com/a")
        resp, body = self.request("GET", "/table")
        self.assertEqual(resp.status, 200)
        self.assertIn("https://example.com/a", body)
        self.assertIn("호너", body)


class TestServerChaining(ServerContract, unittest.TestCase):
    table = "chaining"


class TestTableChoices(unittest.TestCase):
    def test_unknown_table(self):
        with self.assertRaises(ValueError):
            make_server(port=0, table="nope", host="127.0.0.1")

    def test_chaining_listed(self):
        self.assertIn("chaining", [name for name, _ in TABLES])


if __name__ == "__main__":
    unittest.main()
