import os
import sqlite3
from utils import db


def test_save_and_get_scan_results(tmp_path, monkeypatch):
    test_db = tmp_path / "test.db"
    monkeypatch.setenv('DB_PATH', str(test_db))
    hosts = [
        {'ip': '1.1.1.1', 'hostname': 'host', 'mac': '00:11', 'open_ports': [80, 443]},
        {'ip': '2.2.2.2', 'hostname': 'host2', 'mac': '00:22', 'open_ports': []},
    ]
    scan_id = db.save_scan_results(hosts, db_path=str(test_db))
    results = db.get_scan_results(scan_id, db_path=str(test_db))
    assert len(results) == 2
    assert results[0]['ip'] == '1.1.1.1'
    assert 80 in results[0]['open_ports']
