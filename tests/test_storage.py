import unittest
import os
import json
import sqlite3
from src.storage import save_to_json, save_to_sqlite

class TestStorage(unittest.TestCase):
    def test_save_to_json(self):
        test_data = [{"ip": "192.168.1.1", "ports": [[22, "Open"]]}]
        save_to_json(test_data, "results/test.json")
        self.assertTrue(os.path.exists("results/test.json"))

    def test_save_to_sqlite(self):
        test_data = [{"ip": "192.168.1.1", "ports": [[22, "Open"]]}]
        save_to_sqlite(test_data, "data/test.db")
        self.assertTrue(os.path.exists("data/test.db"))

        conn = sqlite3.connect("data/test.db")
        c = conn.cursor()
        c.execute("SELECT * FROM scans")
        rows = c.fetchall()
        self.assertGreaterEqual(len(rows), 1)
        conn.close()

if __name__ == "__main__":
    unittest.main()
