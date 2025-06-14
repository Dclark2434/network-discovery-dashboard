import os
import sqlite3
from utils import db


def test_save_and_get_scan_results(tmp_path, monkeypatch):
    test_db = tmp_path / "test.db"
    monkeypatch.setenv('DB_PATH', str(test_db))
    hosts = [
        {'ip': '1.1.1.1', 'hostname': 'host', 'mac': '00:11', 'os': 'Linux', 'open_ports': [80, 443]},
        {'ip': '2.2.2.2', 'hostname': 'host2', 'mac': '00:22', 'os': 'Linux', 'open_ports': []},
    ]
    scan_id = db.save_scan_results(hosts, db_path=str(test_db))
    results = db.get_scan_results(scan_id, db_path=str(test_db))
    assert len(results) == 2
    assert results[0]['ip'] == '1.1.1.1'
    assert 80 in results[0]['open_ports']


def test_env_var_db_path_used(tmp_path, monkeypatch):
    env_db = tmp_path / "env.db"
    monkeypatch.setenv('DB_PATH', str(env_db))
    hosts = [
        {'ip': '3.3.3.3', 'hostname': 'host3', 'mac': '00:33', 'os': 'Linux', 'open_ports': []}
    ]
    scan_id = db.save_scan_results(hosts)
    results = db.get_scan_results(scan_id)
    assert results[0]['ip'] == '3.3.3.3'
    assert env_db.exists()


def test_get_latest_scan_results(tmp_path):
    db_path = tmp_path / "latest.db"
    hosts1 = [
        {'ip': '1.1.1.1', 'hostname': 'h1', 'mac': 'm1', 'os': 'Linux', 'open_ports': [80]}
    ]
    hosts2 = [
        {'ip': '2.2.2.2', 'hostname': 'h2', 'mac': 'm2', 'os': 'Linux', 'open_ports': [22]}
    ]
    db.save_scan_results(hosts1, db_path=str(db_path))
    db.save_scan_results(hosts2, db_path=str(db_path))
    results = db.get_latest_scan_results(db_path=str(db_path))
    assert len(results) == 1
    assert results[0]['ip'] == '2.2.2.2'


def test_get_latest_scan_results_empty(tmp_path):
    db_path = tmp_path / "empty.db"
    results = db.get_latest_scan_results(db_path=str(db_path))
    assert results == []


def test_get_scan_history(tmp_path):
    db_path = tmp_path / "history.db"
    hosts1 = [{'ip': '1.1.1.1', 'hostname': 'h1', 'mac': 'm1', 'os': 'Linux', 'open_ports': []}]
    hosts2 = [{'ip': '2.2.2.2', 'hostname': 'h2', 'mac': 'm2', 'os': 'Linux', 'open_ports': []}]
    id1 = db.save_scan_results(hosts1, db_path=str(db_path))
    id2 = db.save_scan_results(hosts2, db_path=str(db_path))
    history = db.get_scan_history(db_path=str(db_path))
    assert [record['id'] for record in history] == [id1, id2]


def test_get_scan_history_env_var_used(tmp_path, monkeypatch):
    env_db = tmp_path / "env_history.db"
    monkeypatch.setenv('DB_PATH', str(env_db))
    db.save_scan_results([{'ip': '1.1.1.1', 'hostname': 'h1', 'mac': 'm1', 'os': 'Linux', 'open_ports': []}])
    history = db.get_scan_history()
    assert len(history) == 1
    assert env_db.exists()


def test_db_directory_created(tmp_path):
    db_path = tmp_path / "nested" / "created.db"
    # parent directory does not exist yet
    assert not db_path.parent.exists()
    db.save_scan_results([
        {'ip': '1.1.1.1', 'hostname': 'h', 'mac': 'm', 'os': 'Linux', 'open_ports': []}
    ], db_path=str(db_path))
    # connection should create the directory automatically
    assert db_path.exists()
