import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import json
import sqlite3
from storage import save_to_json, save_to_sqlite

def test_save_to_json(tmp_path):
    sample_data = [{"ip": "192.168.1.1", "ports": [(80, "Open")]}]
    file_path = tmp_path / "test_scans.json"
    save_to_json(sample_data, str(file_path))
    
    with open(file_path, "r") as f:
        data = json.load(f)
    
    assert len(data) == 1
    assert data[0]["results"][0]["ip"] == "192.168.1.1"

def test_save_to_sqlite(tmp_path):
    sample_data = [{"ip": "192.168.1.1", "ports": [(80, "Open"), (22, "Closed")]}]
    db_path = tmp_path / "test_scans.db"
    save_to_sqlite(sample_data, str(db_path))
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM scans")
    count = c.fetchone()[0]
    conn.close()

    assert count == 2
