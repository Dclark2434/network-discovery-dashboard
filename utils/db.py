import sqlite3
import os
from contextlib import contextmanager

DEFAULT_DB_PATH = os.path.join('data', 'devices.db')

def get_db_path() -> str:
    """Return the database path taking into account the DB_PATH env var."""
    return os.environ.get('DB_PATH', DEFAULT_DB_PATH)

@contextmanager
def get_connection(db_path: str = None):
    if db_path is None:
        db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()

def initialize_db(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )"""
    )
    cur.execute(
        """CREATE TABLE IF NOT EXISTS hosts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id INTEGER,
                ip TEXT,
                hostname TEXT,
                mac TEXT,
                open_ports TEXT,
                FOREIGN KEY(scan_id) REFERENCES scans(id)
            )"""
    )
    conn.commit()

def save_scan_results(hosts, db_path: str = None):
    with get_connection(db_path) as conn:
        initialize_db(conn)
        cur = conn.cursor()
        cur.execute("INSERT INTO scans DEFAULT VALUES")
        scan_id = cur.lastrowid
        for host in hosts:
            ports = ','.join(str(p) for p in host.get('open_ports', []))
            cur.execute(
                "INSERT INTO hosts (scan_id, ip, hostname, mac, open_ports) VALUES (?, ?, ?, ?, ?)",
                (scan_id, host.get('ip'), host.get('hostname'), host.get('mac'), ports)
            )
        conn.commit()
        return scan_id

def get_scan_results(scan_id: int, db_path: str = None):
    with get_connection(db_path) as conn:
        initialize_db(conn)
        cur = conn.cursor()
        cur.execute("SELECT ip, hostname, mac, open_ports FROM hosts WHERE scan_id=?", (scan_id,))
        rows = cur.fetchall()
        result = []
        for ip, hostname, mac, ports in rows:
            open_ports = [int(p) for p in ports.split(',') if p]
            result.append({
                'ip': ip,
                'hostname': hostname,
                'mac': mac,
                'open_ports': open_ports
            })
        return result
