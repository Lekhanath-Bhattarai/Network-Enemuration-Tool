# tests/test_scanner.py

import unittest
from src.scanner import ping_ip, scan_port

class TestScanner(unittest.TestCase):
    def test_ping_ip(self):
        result = ping_ip("8.8.8.8")
        self.assertIsInstance(result, bool)

    def test_scan_port(self):
        result = scan_port("127.0.0.1", 22)
        self.assertIsNotNone(result)

if __name__ == "__main__":
    unittest.main()
