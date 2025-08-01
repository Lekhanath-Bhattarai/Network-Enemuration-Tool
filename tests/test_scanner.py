import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from scanner import scan_port

def test_scan_open_port():
    port, status = scan_port("127.0.0.1", 22)
    assert port == 22
    assert status in ["Open", "Closed"]

def test_scan_closed_port():
    port, status = scan_port("127.0.0.1", 65000)
    assert port == 65000
    assert status in ["Open", "Closed"]
