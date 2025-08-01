import json
import sqlite3
from datetime import datetime
import os

def save_to_json(data, filename="results/scans.json"):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    timestamp = datetime.now().isoformat()
    record = {"timestamp": timestamp, "results": data}

    try:
        with open(filename, "r") as f:
            all_data = json.load(f)
    except FileNotFoundError:
        all_data = []

    all_data.append(record)

    with open(filename, "w") as f:
        json.dump(all_data, f, indent=4)

def save_to_sqlite(data, db_file="data/scans.db"):
    os.makedirs(os.path.dirname(db_file), exist_ok=True)
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS scans (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     target TEXT,
                     port INTEGER,
                     status TEXT,
                     timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')

    for entry in data:
        for port_result in entry["ports"]:
            c.execute("INSERT INTO scans (target, port, status) VALUES (?, ?, ?)",
                      (entry["ip"], port_result[0], port_result[1]))

    conn.commit()
    conn.close()
